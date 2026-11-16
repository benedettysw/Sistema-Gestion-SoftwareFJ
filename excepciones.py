import logging
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS (REGISTRO DE EVENTOS Y ERRORES)
# ==============================================================================
# Configuramos el módulo logging para guardar todos los eventos y errores
# en un archivo de texto llamado 'sistema_fj.log' sin detener la ejecución.
logging.basicConfig(
    filename="sistema_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)


def registrar_evento(mensaje: str, nivel: str = "INFO") -> None:
    """
    Registra un evento o error tanto en el archivo de logs como en la consola
    para mantener trazabilidad de la ejecución del sistema.
    """
    if nivel.upper() == "ERROR":
        logging.error(mensaje)
        print(f"[ERROR LOGGED] {mensaje}")
    elif nivel.upper() == "WARNING":
        logging.warning(mensaje)
        print(f"[ADVERTENCIA] {mensaje}")
    else:
        logging.info(mensaje)
        print(f"[INFO] {mensaje}")


# ==============================================================================
# 2. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# ==============================================================================
class ErrorSistemaFJ(Exception):
    """
    Excepción base personalizada para todos los errores controlados
    dentro del sistema de gestión de Software FJ.
    """
    def __init__(self, mensaje: str, codigo_error: str = "ERR-000"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        return f"[{self.codigo_error}] ({self.fecha_hora}) -> {self.mensaje}"


class DatoInvalidoError(ErrorSistemaFJ):
    """Se lanza cuando un dato ingresado no cumple el formato o reglas (ej. correo, nombre vacío)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-DATO-001")


class ParametroFaltanteError(ErrorSistemaFJ):
    """Se lanza cuando faltan parámetros obligatorios para crear una entidad o calcular costos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-PARAM-002")


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando se intenta reservar un servicio inactivo o sin cupo/stock."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-SERV-003")


class ReservaInvalidaError(ErrorSistemaFJ):
    """Se lanza cuando una operación de reserva no es permitida (ej. cancelar una ya cancelada)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-RES-004")


class CalculoInconsistenteError(ErrorSistemaFJ):
    """Se lanza cuando ocurre un fallo matemático o valores negativos en tarifas/impuestos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-CALC-005")