from abc import ABC, abstractmethod
import uuid
from datetime import datetime
from exceptions import (
    InvalidDataError, 
    MissingParameterError, 
    CalculationError, 
    InvalidReservationError, 
    ServiceUnavailableError
)

# Clase abstracta que representa entidades generales del sistema
class SystemEntity(ABC):
    """
    Clase base abstracta para todas las entidades del sistema.
    Fuerza a las clases derivadas a implementar un método de representación en texto.
    """
    def __init__(self):
        # Generamos un ID único para cada entidad
        self._id = str(uuid.uuid4())

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def get_details(self) -> str:
        """
        Método abstracto para obtener los detalles de la entidad.
        Debe ser implementado por todas las subclases.
        """
        pass


class Client(SystemEntity):
    """
    Clase que representa a un cliente. Implementa encapsulación y validación estricta de datos.
    """
    def __init__(self, name: str, email: str, phone: str):
        super().__init__()
        
        # Validaciones de los parámetros de entrada
        if not name or not email or not phone:
            raise MissingParameterError("Name, email and phone are required for a Client.")
        if not isinstance(name, str) or not isinstance(email, str) or not isinstance(phone, str):
            raise InvalidDataError("Client data must be strings.")
            
        # Encapsulación de los atributos personales
        self._name = name
        self._email = email
        self._phone = phone

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value:
            raise InvalidDataError("Name cannot be empty.")
        self._name = value

    @property
    def email(self) -> str:
        return self._email

    @property
    def phone(self) -> str:
        return self._phone

    def get_details(self) -> str:
        """
        Retorna los detalles encapsulados del cliente.
        """
        return f"Client: {self._name} | Email: {self._email} | Phone: {self._phone}"


class Service(SystemEntity):
    """
    Clase abstracta para servicios generales.
    Define la base para el polimorfismo en el cálculo de costos.
    """
    def __init__(self, name: str, base_price: float):
        super().__init__()
        if not name:
            raise MissingParameterError("Service name is required.")
        if base_price < 0:
            raise InvalidDataError("Base price cannot be negative.")
        
        self.name = name
        self.base_price = base_price
        self.is_available = True

    @abstractmethod
    def calculate_cost(self, *args, **kwargs) -> float:
        """
        Método abstracto para calcular costos. 
        Utiliza *args y **kwargs para simular sobrecarga de métodos en subclases.
        """
        pass

    def get_details(self) -> str:
        return f"Service: {self.name} | Base Price: ${self.base_price:.2f} | Available: {self.is_available}"


class RoomService(Service):
    """
    Servicio de reserva de salas.
    """
    def __init__(self, name: str, base_price: float, capacity: int):
        super().__init__(name, base_price)
        if capacity <= 0:
            raise InvalidDataError("Capacity must be greater than zero.")
        self.capacity = capacity

    def calculate_cost(self, hours: int, apply_taxes: bool = True) -> float:
        """
        Sobrecarga simulada mediante parámetros por defecto.
        Calcula el costo en función de las horas y opcionalmente aplica impuestos.
        """
        if type(hours) not in (int, float) or hours <= 0:
            raise CalculationError("Hours must be a positive number.")
            
        cost = float(self.base_price * hours)
        if apply_taxes:
            cost *= 1.19  # Aplicamos un 19% de impuestos simulado
        return cost

    def get_details(self) -> str:
        base = super().get_details()
        return f"{base} | Type: Room | Capacity: {self.capacity} persons"


class EquipmentService(Service):
    """
    Servicio de alquiler de equipos.
    """
    def __init__(self, name: str, base_price: float, equipment_type: str):
        super().__init__(name, base_price)
        if not equipment_type:
            raise MissingParameterError("Equipment type is required.")
        self.equipment_type = equipment_type

    def calculate_cost(self, days: int, discount_percentage: float = 0.0) -> float:
        """
        Sobrecarga simulada.
        Calcula el costo por días con un posible porcentaje de descuento.
        """
        if type(days) not in (int, float) or days <= 0:
            raise CalculationError("Days must be a positive number.")
        if type(discount_percentage) not in (int, float) or discount_percentage < 0 or discount_percentage > 100:
            raise CalculationError("Discount percentage must be between 0 and 100.")
            
        cost = float(self.base_price * days)
        discount = cost * (discount_percentage / 100.0)
        return cost - discount

    def get_details(self) -> str:
        base = super().get_details()
        return f"{base} | Type: Equipment ({self.equipment_type})"


class ConsultingService(Service):
    """
    Servicio de asesorías especializadas.
    """
    def __init__(self, name: str, base_price: float, consultant_name: str):
        super().__init__(name, base_price)
        if not consultant_name:
            raise MissingParameterError("Consultant name is required.")
        self.consultant_name = consultant_name

    def calculate_cost(self, sessions: int, is_premium: bool = False) -> float:
        """
        Sobrecarga simulada.
        Calcula el costo por sesiones, con un recargo adicional si es categoría premium.
        """
        if type(sessions) not in (int, float) or sessions <= 0:
            raise CalculationError("Sessions must be a positive number.")
            
        cost = float(self.base_price * sessions)
        if is_premium:
            cost += 50.0  # Cargo fijo por ser premium
        return cost

    def get_details(self) -> str:
        base = super().get_details()
        return f"{base} | Type: Consulting | Consultant: {self.consultant_name}"


class Reservation(SystemEntity):
    """
    Clase que integra cliente, servicio, duración y estado.
    Implementa la confirmación y cancelación de manera segura utilizando manejo de excepciones.
    """
    def __init__(self, client: Client, service: Service, duration: int):
        super().__init__()
        if not isinstance(client, Client):
            raise InvalidDataError("A valid Client object is required.")
        if not isinstance(service, Service):
            raise InvalidDataError("A valid Service object is required.")
        if type(duration) not in (int, float) or duration <= 0:
            raise InvalidDataError("Duration must be a positive number.")
            
        self.client = client
        self.service = service
        self.duration = duration
        self.status = "Pending"
        self.total_cost = 0.0
        self.created_at = datetime.now()

    def confirm(self, **kwargs):
        """
        Confirma la reserva calculando el costo del servicio asociado.
        """
        if self.status != "Pending":
            raise InvalidReservationError(f"Reservation cannot be confirmed because it is '{self.status}'.")
            
        if not self.service.is_available:
            raise ServiceUnavailableError(f"Service '{self.service.name}' is currently unavailable.")
            
        # Intentamos calcular el costo del servicio
        try:
            self.total_cost = self.service.calculate_cost(self.duration, **kwargs)
        except Exception as e:
            # Encadenamiento de excepciones: encapsulamos errores de cálculo dentro de un error de reserva
            raise CalculationError(f"Failed to confirm reservation due to calculation error.") from e
        else:
            # Si el cálculo es exitoso, confirmamos la reserva
            self.status = "Confirmed"

    def cancel(self):
        """
        Cancela la reserva si es posible.
        """
        if self.status == "Cancelled":
            raise InvalidReservationError("Reservation is already cancelled.")
            
        self.status = "Cancelled"

    def get_details(self) -> str:
        return (f"Reservation [{self.status}] | Client: {self.client.name} | "
                f"Service: {self.service.name} | Duration: {self.duration} | Cost: ${self.total_cost:.2f}")
