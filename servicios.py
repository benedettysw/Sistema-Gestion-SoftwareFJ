from modelos_base import Servicio
from excepciones import (
    DatoInvalidoError,
    CalculoInconsistenteError,
    ServicioNoDisponibleError,
    registrar_evento
)


# ==============================================================================
# 1. SERVICIO ESPECIALIZADO: RESERVA DE SALAS
# ==============================================================================
class ReservaSala(Servicio):
    """
    Servicio especializado para el alquiler de salas de reuniones o capacitación.
    Implementa validaciones de capacidad y recargos opcionales por catering/equipos.
    """
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_hora: float, capacidad: int, disponible: bool = True):
        super().__init__(id_servicio, nombre_servicio, tarifa_hora, disponible)
        if capacidad <= 0:
            raise DatoInvalidoError(f"La capacidad de la sala ({capacidad}) debe ser mayor a 0.")
        self._capacidad = capacidad
        registrar_evento(f"Servicio creado -> Sala: {self.nombre_servicio} (Capacidad: {self._capacidad} personas)")

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_parametros(self, duracion: int) -> None:
        if not self.disponible:
            raise ServicioNoDisponibleError(f"La sala '{self.nombre_servicio}' no está disponible actualmente.")
        if duracion < 1 or duracion > 12:
            raise DatoInvalidoError(f"Duración inválida ({duracion}h): una sala se reserva entre 1 y 12 horas.")

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0, costo_catering: float = 0.0) -> float:
        """
        Sobrecarga simulada: permite calcular el costo solo con duración,
        o incluyendo impuestos, descuentos y servicio opcional de catering.
        """
        self.validar_parametros(duracion)
        if impuesto < 0 or descuento < 0 or descuento > 0.50 or costo_catering < 0:
            raise CalculoInconsistenteError("Parámetros financieros inválidos en cálculo de sala (descuento máx 50%).")

        subtotal = (self.tarifa_base * duracion) + costo_catering
        subtotal_con_descuento = subtotal * (1 - descuento)
        total = subtotal_con_descuento * (1 + impuesto)
        return round(total, 2)

    def obtener_resumen(self) -> str:
        return f"{super().obtener_resumen()} | Tipo: Sala (Capacidad: {self._capacidad} pers.)"


# ==============================================================================
# 2. SERVICIO ESPECIALIZADO: ALQUILER DE EQUIPOS
# ==============================================================================
class AlquilerEquipo(Servicio):
    """
    Servicio especializado para el alquiler de hardware (laptops, proyectores, servidores).
    Incluye validación de inventario (stock) y seguro obligatorio por daño.
    """
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_dia: float, stock_disponible: int, seguro_diario: float = 15000.0):
        super().__init__(id_servicio, nombre_servicio, tarifa_dia, disponible=(stock_disponible > 0))
        if stock_disponible < 0:
            raise DatoInvalidoError("El stock inicial de equipos no puede ser negativo.")
        if seguro_diario < 0:
            raise CalculoInconsistenteError("El valor del seguro diario no puede ser negativo.")

        self._stock = stock_disponible
        self._seguro_diario = seguro_diario
        registrar_evento(f"Servicio creado -> Equipo: {self.nombre_servicio} (Stock: {self._stock} unidades)")

    @property
    def stock(self) -> int:
        return self._stock

    def descontar_stock(self) -> None:
        if self._stock <= 0:
            self.disponible = False
            raise ServicioNoDisponibleError(f"Sin unidades disponibles para '{self.nombre_servicio}'.")
        self._stock -= 1
        if self._stock == 0:
            self.disponible = False

    def restaurar_stock(self) -> None:
        self._stock += 1
        self.disponible = True

    def validar_parametros(self, duracion: int) -> None:
        if not self.disponible or self._stock <= 0:
            raise ServicioNoDisponibleError(f"El equipo '{self.nombre_servicio}' está agotado o inactivo.")
        if duracion < 1 or duracion > 30:
            raise DatoInvalidoError(f"Duración inválida ({duracion} días): el alquiler es de 1 a 30 días.")

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0, incluir_seguro: bool = True) -> float:
        """
        Sobrecarga simulada: permite incluir o eximir el seguro diario
        además de impuestos y descuentos por alquiler prolongado.
        """
        self.validar_parametros(duracion)
        if impuesto < 0 or descuento < 0 or descuento > 0.40:
            raise CalculoInconsistenteError("Parámetros financieros inválidos en cálculo de equipo (descuento máx 40%).")

        costo_seguro = (self._seguro_diario * duracion) if incluir_seguro else 0.0
        subtotal = (self.tarifa_base * duracion) + costo_seguro
        subtotal_con_descuento = subtotal * (1 - descuento)
        total = subtotal_con_descuento * (1 + impuesto)
        return round(total, 2)

    def obtener_resumen(self) -> str:
        return f"{super().obtener_resumen()} | Tipo: Equipo (Stock: {self._stock} unid.)"


# ==============================================================================
# 3. SERVICIO ESPECIALIZADO: ASESORÍA ESPECIALIZADA
# ==============================================================================
class AsesoriaEspecializada(Servicio):
    """
    Servicio especializado de consultoría técnica (Arquitectura, Cloud, Seguridad).
    Aplica recargo si se solicita en modalidad urgente/prioritaria.
    """
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_hora: float, area_tecnica: str, disponible: bool = True):
        super().__init__(id_servicio, nombre_servicio, tarifa_hora, disponible)
        if not area_tecnica or not area_tecnica.strip():
            raise DatoInvalidoError("Debe especificar el área técnica de la asesoría.")
        self._area_tecnica = area_tecnica.strip()
        registrar_evento(f"Servicio creado -> Asesoría: {self.nombre_servicio} (Área: {self._area_tecnica})")

    @property
    def area_tecnica(self) -> str:
        return self._area_tecnica

    def validar_parametros(self, duracion: int) -> None:
        if not self.disponible:
            raise ServicioNoDisponibleError(f"La asesoría '{self.nombre_servicio}' no tiene consultores disponibles.")
        if duracion < 2:
            raise DatoInvalidoError(f"Duración inválida ({duracion}h): las asesorías requieren mínimo 2 horas.")

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0, urgente: bool = False) -> float:
        """
        Sobrecarga simulada: aplica un recargo del 25% si la asesoría es urgente.
        """
        self.validar_parametros(duracion)
        if impuesto < 0 or descuento < 0 or descuento > 0.30:
            raise CalculoInconsistenteError("Parámetros financieros inválidos en asesoría (descuento máx 30%).")

        recargo_urgencia = 1.25 if urgente else 1.0
        subtotal = (self.tarifa_base * duracion) * recargo_urgencia
        subtotal_con_descuento = subtotal * (1 - descuento)
        total = subtotal_con_descuento * (1 + impuesto)
        return round(total, 2)

    def obtener_resumen(self) -> str:
        return f"{super().obtener_resumen()} | Tipo: Asesoría ({self._area_tecnica})"