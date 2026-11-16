from gestion import SistemaSoftwareFJ
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from excepciones import ErrorSistemaFJ, registrar_evento


def ejecutar_simulacion() -> None:
    """
    Ejecuta 12 operaciones completas (válidas e inválidas) sobre el sistema
    Software FJ, demostrando estabilidad, polimorfismo y registro en logs.
    """
    sistema = SistemaSoftwareFJ()

    print("\n--- INICIANDO SIMULACIÓN DE OPERACIONES EN SOFTWARE FJ ---\n")

    # ==========================================================================
    # BLOQUE A: REGISTRO DE CLIENTES (VÁLIDOS E INVÁLIDOS)
    # ==========================================================================
    # Operación 1: Registro de cliente válido 1
    sistema.registrar_cliente("CLI-01", "Laura Martínez", "1045678912", "laura.martinez@empresa.com")

    # Operación 2: Registro de cliente válido 2
    sistema.registrar_cliente("CLI-02", "Carlos Gómez", "72345890", "cgomez@techcolombia.co")

    # Operación 3: Registro inválido (correo sin formato válido y documento corto -> dispara DatoInvalidoError)
    sistema.registrar_cliente("CLI-03", "Ana", "123", "correo_invalido_sin_arroba")

    # Operación 4: Registro inválido por documento duplicado
    sistema.registrar_cliente("CLI-04", "Laura Clon", "1045678912", "otro@correo.com")

    # ==========================================================================
    # BLOQUE B: CREACIÓN DE SERVICIOS ESPECIALIZADOS (POLIMORFISMO)
    # ==========================================================================
    # Operación 5: Creación válida de los 3 tipos de servicios requeridos
    try:
        sala_juntas = ReservaSala("SRV-01", "Sala Ejecutiva Norte", tarifa_hora=80000.0, capacidad=15)
        laptop_pro = AlquilerEquipo("SRV-02", "Workstation Ryzen 7", tarifa_dia=65000.0, stock_disponible=1)
        asesoria_cloud = AsesoriaEspecializada("SRV-03", "Arquitectura Cloud AWS", tarifa_hora=120000.0, area_tecnica="Cloud & DevOps")

        sistema.agregar_servicio(sala_juntas)
        sistema.agregar_servicio(laptop_pro)
        sistema.agregar_servicio(asesoria_cloud)
    except ErrorSistemaFJ as err:
        registrar_evento(f"Error inesperado creando catálogo base: {err}", nivel="ERROR")

    # Operación 6: Creación inválida de servicio (tarifa negativa -> dispara CalculoInconsistenteError)
    try:
        sala_mala = ReservaSala("SRV-99", "Sala Defectuosa", tarifa_hora=-50000.0, capacidad=10)
        sistema.agregar_servicio(sala_mala)
    except ErrorSistemaFJ as err:
        registrar_evento(f"Fallo controlado al instanciar servicio inválido: {err}", nivel="ERROR")

    # ==========================================================================
    # BLOQUE C: PROCESAMIENTO DE RESERVAS (EXITOSAS, SOBRECARGA Y FALLIDAS)
    # ==========================================================================
    # Operación 7: Reserva exitosa de sala con parámetros opcionales (descuento 10% + catering)
    reserva_1 = sistema.crear_y_confirmar_reserva(
        id_reserva="RES-101",
        id_cliente="CLI-01",
        id_servicio="SRV-01",
        duracion=4,
        descuento=0.10,
        costo_catering=50000.0
    )

    # Operación 8: Reserva exitosa de equipo (consume la única unidad disponible en stock)
    reserva_2 = sistema.crear_y_confirmar_reserva(
        id_reserva="RES-102",
        id_cliente="CLI-02",
        id_servicio="SRV-02",
        duracion=3,
        incluir_seguro=True
    )

    # Operación 9: Reserva fallida por falta de stock (el equipo SRV-02 ya quedó en stock 0)
    sistema.crear_y_confirmar_reserva(
        id_reserva="RES-103",
        id_cliente="CLI-01",
        id_servicio="SRV-02",
        duracion=2
    )

    # Operación 10: Reserva fallida por duración inválida en asesoría (mínimo son 2 horas, se envía 1)
    sistema.crear_y_confirmar_reserva(
        id_reserva="RES-104",
        id_cliente="CLI-02",
        id_servicio="SRV-03",
        duracion=1,
        urgente=True
    )

    # Operación 11: Reserva exitosa de asesoría urgente (3 horas)
    reserva_3 = sistema.crear_y_confirmar_reserva(
        id_reserva="RES-105",
        id_cliente="CLI-01",
        id_servicio="SRV-03",
        duracion=3,
        urgente=True
    )

    # ==========================================================================
    # BLOQUE D: CANCELACIÓN Y DOBLE CANCELACIÓN CONTROLADA
    # ==========================================================================
    # Operación 12: Cancelar reserva_2 (restaura stock del equipo) e intentar cancelarla de nuevo
    if reserva_2:
        try:
            reserva_2.cancelar()
            # Intentamos cancelar por segunda vez para probar ReservaInvalidaError
            reserva_2.cancelar()
        except ErrorSistemaFJ as err:
            registrar_evento(f"Control de doble cancelación exitoso: {err}", nivel="ERROR")

    # ==========================================================================
    # REPORTE FINAL EN CONSOLA
    # ==========================================================================
    sistema.generar_reporte_consola()
    registrar_evento("=== FIN DE LA SIMULACIÓN - SISTEMA ESTABLE Y SIN INTERRUPCIONES ===")


if __name__ == "__main__":
    ejecutar_simulacion()