from abc import ABC, abstractmethod
from datetime import datetime
import re
from excepciones import (
    DatoInvalidoError,
    ParametroFaltanteError,
    CalculoInconsistenteError,
    registrar_evento
)


# ==============================================================================
# 1. CLASE ABSTRACTA QUE REPRESENTA ENTIDADES GENERALES DEL SISTEMA
# ==============================================================================
class EntidadBase(ABC):
    """
    Clase abstracta base para todas las entidades del sistema Software FJ
    (Clientes, Servicios, Reservas). Garantiza identificación y trazabilidad.
    """
    def __init__(self, id_entidad: str):
        if not id_entidad or not str(id_entidad).strip():
            raise ParametroFaltanteError("El ID de la entidad es obligatorio y no puede estar vacío.")
        self._id = str(id_entidad).strip()
        self._fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def id(self) -> str:
        """Encapsulación: permite leer el ID sin modificarlo directamente."""
        return self._id

    @property
    def fecha_creacion(self) -> str:
        """Retorna la fecha y hora de creación de la entidad."""
        return self._fecha_creacion

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Método abstracto que obliga a las clases hijas a describirse."""
        pass


# ==============================================================================
# 2. CLASE CLIENTE CON ENCAPSULACIÓN Y VALIDACIONES ESTRICTAS
# ==============================================================================
class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ con validación estricta de datos personales
    y encapsulación mediante propiedades (@property).
    """
    def __init__(self, id_cliente: str, nombre: str, documento: str, correo: str):
        super().__init__(id_cliente)
        # Se asignan usando los setters para disparar las validaciones desde el inicio
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        registrar_evento(f"Cliente registrado correctamente: {self.nombre} (ID: {self.id})")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or len(valor.strip()) < 3:
            raise DatoInvalidoError(f"Nombre inválido ('{valor}'): debe tener al menos 3 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        doc_limpio = str(valor).strip()
        if not doc_limpio.isdigit() or len(doc_limpio) < 6:
            raise DatoInvalidoError(f"Documento inválido ('{valor}'): debe contener solo números (mínimo 6 dígitos).")
        self._documento = doc_limpio

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not valor or not re.match(patron_email, valor.strip()):
            raise DatoInvalidoError(f"Correo electrónico inválido ('{valor}').")
        self._correo = valor.strip().lower()

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id}] | {self.nombre} | Doc: {self.documento} | Email: {self.correo}"


# ==============================================================================
# 3. CLASE ABSTRACTA SERVICIO
# ==============================================================================
class Servicio(EntidadBase, ABC):
    """
    Clase abstracta base para los servicios ofrecidos por Software FJ.
    Define la interfaz común para polimorfismo y cálculo de tarifas.
    """
    def __init__(self, id_servicio: str, nombre_servicio: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_servicio)
        if not nombre_servicio or not nombre_servicio.strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if tarifa_base is None or float(tarifa_base) <= 0:
            raise CalculoInconsistenteError(f"La tarifa base ({tarifa_base}) debe ser mayor a cero.")

        self._nombre_servicio = nombre_servicio.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def nombre_servicio(self) -> str:
        return self._nombre_servicio

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion: int) -> None:
        """Valida reglas específicas de cada servicio (ej. horas mínimas o máximas)."""
        pass

    @abstractmethod
    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """
        Método polimórfico y con parámetros opcionales (sobrecarga simulada)
        para calcular el costo total con impuestos y descuentos.
        """
        pass

    def obtener_resumen(self) -> str:
        estado_txt = "Disponible" if self._disponible else "No Disponible"
        return f"Servicio [{self.id}] {self.nombre_servicio} - Tarifa base: ${self.tarifa_base:,.2f} ({estado_txt})"