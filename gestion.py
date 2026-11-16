from modelos_base import EntidadBase, Cliente, Servicio
from servicios import AlquilerEquipo
from excepciones import (
    ErrorSistemaFJ,
    DatoInvalidoError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    registrar_evento
)


# ==============================================================================
# 1. CLASE RESERVA (INTEGRA CLIENTE, SERVICIO, DURACIÓN Y ESTADO)
# ==============================================================================
class Reserva(EntidadBase):
    """
    Gestiona el ciclo de vida de una reserva (PENDIENTE -> CONFIRMADA / CANCELADA).
    Implementa confirmación, cancelación y cálculo de costos con manejo de excepciones.
    """
    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int, **opciones_costo):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ParametroFaltanteError("Debe asociar una instancia válida de Cliente a la reserva.")
        if not isinstance(servicio, Servicio):
            raise ParametroFaltanteError("Debe asociar una instancia válida de Servicio a la reserva.")
        if not isinstance(duracion, int) or duracion <= 0:
            raise DatoInvalidoError(f"La duración ({duracion}) debe ser un número entero positivo.")

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._opciones_costo = opciones_costo
        self._estado = "PENDIENTE"
        self._costo_total = 0.0

        # Validamos y calculamos el costo inicial usando encadenamiento de excepciones
        self.procesar_calculo()

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> int:
        return self._duracion

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def procesar_calculo(self) -> float:
        """
        Calcula el costo delegando al método polimórfico del servicio.
        Aplica encadenamiento de excepciones (raise ... from ...) para trazabilidad.
        """
        try:
            self._costo_total = self._servicio.calcular_costo(self._duracion, **self._opciones_costo)
            return self._costo_total
        except ErrorSistemaFJ as err:
            # Encadenamiento de excepción: conserva la causa original dentro de ReservaInvalidaError
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva [{self.id}] para '{self._servicio.nombre_servicio}'."
            ) from err

    def confirmar(self) -> None:
        """Confirma una reserva pendiente y descuenta inventario si aplica."""
        if self._estado == "CONFIRMADA":
            raise ReservaInvalidaError(f"La reserva [{self.id}] ya se encuentra CONFIRMADA.")
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError(f"No se puede confirmar la reserva [{self.id}] porque está CANCELADA.")

        # Si el servicio es un equipo físico, descontamos una unidad del stock
        if isinstance(self._servicio, AlquilerEquipo):
            self._servicio.descontar_stock()

        self._estado = "CONFIRMADA"
        registrar_evento(
            f"Reserva [{self.id}] CONFIRMADA | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre_servicio} | Total: ${self._costo_total:,.2f}"
        )

    def cancelar(self) -> None:
        """Cancela una reserva activa y restaura stock si estaba confirmada."""
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError(f"Operación no permitida: la reserva [{self.id}] ya fue CANCELADA.")

        if self._estado == "CONFIRMADA" and isinstance(self._servicio, AlquilerEquipo):
            self._servicio.restaurar_stock()

        self._estado = "CANCELADA"
        registrar_evento(f"Reserva [{self.id}] CANCELADA por solicitud del cliente {self._cliente.nombre}.", nivel="WARNING")

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self.id}] | Estado: {self._estado} | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre_servicio} ({self._duracion} unid.) | Total: ${self._costo_total:,.2f}"
        )


# ==============================================================================
# 2. CONTROLADOR CENTRAL DEL SISTEMA (GESTIÓN EN MEMORIA SIN BASE DE DATOS)
# ==============================================================================
class SistemaSoftwareFJ:
    """
    Administra las listas internas de clientes, servicios y reservas en memoria.
    Garantiza que los errores sean capturados, registrados y controlados sin detener la app.
    """
    def __init__(self):
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []
        registrar_evento("=== INICIO DEL SISTEMA INTEGRAL SOFTWARE FJ (MODO MEMORIA) ===")

    def registrar_cliente(self, id_cliente: str, nombre: str, documento: str, correo: str) -> Cliente | None:
        """Registra un cliente usando estructura completa try / except / else / finally."""
        nuevo_cliente = None
        try:
            # Verificar duplicados por ID o documento
            if any(c.id == id_cliente or c.documento == str(documento).strip() for c in self._clientes):
                raise DatoInvalidoError(f"Ya existe un cliente registrado con ID '{id_cliente}' o documento '{documento}'.")
            nuevo_cliente = Cliente(id_cliente, nombre, documento, correo)
        except ErrorSistemaFJ as err:
            registrar_evento(f"Fallo al registrar cliente: {err}", nivel="ERROR")
        else:
            # Solo se ejecuta si el bloque try no lanzó ninguna excepción
            self._clientes.append(nuevo_cliente)
        finally:
            # Se ejecuta siempre para auditoría de control
            registrar_evento(f"Auditoría registro cliente [{id_cliente}] finalizada. Total clientes: {len(self._clientes)}")
        return nuevo_cliente

    def agregar_servicio(self, servicio: Servicio) -> bool:
        """Agrega un servicio validado a la lista interna del catálogo."""
        try:
            if not isinstance(servicio, Servicio):
                raise ParametroFaltanteError("El objeto proporcionado no es un Servicio válido.")
            if any(s.id == servicio.id for s in self._servicios):
                raise DatoInvalidoError(f"El ID de servicio '{servicio.id}' ya existe en el catálogo.")
        except ErrorSistemaFJ as err:
            registrar_evento(f"Fallo al agregar servicio: {err}", nivel="ERROR")
            return False
        else:
            self._servicios.append(servicio)
            return True

    def crear_y_confirmar_reserva(self, id_reserva: str, id_cliente: str, id_servicio: str, duracion: int, **opciones_costo) -> Reserva | None:
        """Busca cliente y servicio en listas, crea la reserva y la confirma de forma segura."""
        reserva = None
        try:
            cliente = next((c for c in self._clientes if c.id == id_cliente), None)
            if cliente is None:
                raise ParametroFaltanteError(f"No se encontró el cliente con ID '{id_cliente}'.")

            servicio = next((s for s in self._servicios if s.id == id_servicio), None)
            if servicio is None:
                raise ServicioNoDisponibleError(f"No se encontró el servicio con ID '{id_servicio}'.")

            reserva = Reserva(id_reserva, cliente, servicio, duracion, **opciones_costo)
            reserva.confirmar()
        except ErrorSistemaFJ as err:
            causa = f" | Causa raíz: {err.__cause__}" if err.__cause__ else ""
            registrar_evento(f"Fallo en operación de reserva [{id_reserva}]: {err}{causa}", nivel="ERROR")
            reserva = None
        else:
            self._reservas.append(reserva)
        finally:
            registrar_evento(f"Cierre de transacción reserva [{id_reserva}]. Reservas activas: {len(self._reservas)}")
        return reserva

    def generar_reporte_consola(self) -> None:
        """Muestra el estado actual de todas las listas en memoria."""
        print("\n" + "=" * 75)
        print("RESUMEN GENERAL EN MEMORIA - SOFTWARE FJ")
        print("=" * 75)
        print(f"\n--- CLIENTES REGISTRADOS ({len(self._clientes)}) ---")
        for c in self._clientes:
            print("  •", c.obtener_resumen())

        print(f"\n--- CATÁLOGO DE SERVICIOS ({len(self._servicios)}) ---")
        for s in self._servicios:
            print("  •", s.obtener_resumen())

        print(f"\n--- HISTORIAL DE RESERVAS ({len(self._reservas)}) ---")
        for r in self._reservas:
            print("  •", r.obtener_resumen())
        print("=" * 75 + "\n")