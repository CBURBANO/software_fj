# Clase base para todas las excepciones del sistema
class SystemErrorBase(Exception):
    """
    Excepción base para el sistema Software FJ.
    Todas las demás excepciones heredan de esta clase para permitir
    un manejo centralizado si es necesario.
    """
    def __init__(self, message="System Error"):
        super().__init__(message)
        self.message = message


class InvalidDataError(SystemErrorBase):
    """
    Lanzada cuando se proporcionan datos inválidos (por ejemplo, tipos de datos incorrectos).
    """
    def __init__(self, message="Invalid data provided"):
        super().__init__(message)


class MissingParameterError(SystemErrorBase):
    """
    Lanzada cuando falta un parámetro obligatorio en una función o creación de objeto.
    """
    def __init__(self, message="Missing required parameter"):
        super().__init__(message)


class ServiceUnavailableError(SystemErrorBase):
    """
    Lanzada cuando un servicio solicitado no está disponible.
    """
    def __init__(self, message="The requested service is unavailable"):
        super().__init__(message)


class InvalidReservationError(SystemErrorBase):
    """
    Lanzada cuando una reserva no puede ser creada o procesada (ej. fechas inválidas).
    """
    def __init__(self, message="Invalid reservation details"):
        super().__init__(message)


class CalculationError(SystemErrorBase):
    """
    Lanzada cuando ocurre un error durante el cálculo de costos (ej. valores negativos inesperados).
    """
    def __init__(self, message="Error calculating cost"):
        super().__init__(message)
