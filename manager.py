import logging
from models import Client, Service, RoomService, EquipmentService, ConsultingService, Reservation
from exceptions import SystemErrorBase, InvalidDataError

class SystemManager:
    """
    Clase principal que administra las entidades del sistema (clientes, servicios, reservas).
    Maneja las listas en memoria y proporciona métodos para interactuar con ellas,
    asegurando que todos los errores queden registrados en un archivo log.
    """
    def __init__(self):
        self.clients = []
        self.services = []
        self.reservations = []
        
        # Configuración del logger
        self.setup_logger()
        self.logger.info("SystemManager initialized.")

    def setup_logger(self):
        """
        Configura el registro (logging) de eventos y errores en un archivo llamado 'system_log.txt'.
        """
        self.logger = logging.getLogger("SoftwareFJ")
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar agregar múltiples handlers si se inicializa más de una vez
        if not self.logger.handlers:
            fh = logging.FileHandler("system_log.txt", encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def add_client(self, name: str, email: str, phone: str) -> Client:
        """
        Crea y añade un cliente a la lista, con manejo de excepciones.
        """
        try:
            client = Client(name, email, phone)
        except SystemErrorBase as e:
            self.logger.error(f"Failed to add client ({name}): {str(e)}")
            raise
        except Exception as e:
            self.logger.critical(f"Unexpected error adding client: {str(e)}")
            raise
        else:
            # try/except/else: Este bloque se ejecuta solo si no hubo excepciones en el try
            self.clients.append(client)
            self.logger.info(f"Client added successfully: {client.id} - {client.name}")
            return client

    def add_service(self, service: Service) -> Service:
        """
        Añade un servicio a la lista.
        """
        if not isinstance(service, Service):
            msg = "Attempted to add an invalid service object."
            self.logger.error(msg)
            raise InvalidDataError(msg)
        self.services.append(service)
        self.logger.info(f"Service added successfully: {service.name}")
        return service

    def create_reservation(self, client: Client, service: Service, duration: int) -> Reservation:
        """
        Crea una reserva en estado 'Pending'.
        """
        try:
            reservation = Reservation(client, service, duration)
        except Exception as e:
            self.logger.error(f"Failed to create reservation: {str(e)}")
            raise
        else:
            self.reservations.append(reservation)
            self.logger.info(f"Reservation created: {reservation.id} for {client.name}")
            return reservation

    def confirm_reservation(self, reservation: Reservation, **kwargs):
        """
        Confirma una reserva y procesa los posibles errores.
        Muestra uso de try/except/finally.
        """
        try:
            reservation.confirm(**kwargs)
        except SystemErrorBase as e:
            self.logger.error(f"Error confirming reservation {reservation.id}: {str(e)}")
            # Relanzar para que la interfaz gráfica pueda notificar al usuario (si es invocada desde allí)
            raise
        finally:
            # try/except/finally: El bloque finally siempre se ejecuta, útil para auditoría o limpieza
            self.logger.debug(f"Confirmation attempt finished for reservation: {reservation.id}")
            
    def run_simulation(self) -> list:
        """
        Simula 10 operaciones completas, registrando éxitos y fallos intencionados 
        para demostrar el manejo de excepciones y la estabilidad del sistema.
        Retorna un resumen de los resultados.
        """
        results = []
        self.logger.info("--- STARTING SIMULATION OF 10 OPERATIONS ---")
        
        # 1. Operación válida: Crear cliente válido
        try:
            c1 = self.add_client("John Doe", "john@example.com", "555-0100")
            results.append("1. SUCCESS: Valid client created.")
        except Exception as e:
            results.append(f"1. FAILED: {str(e)}")
            
        # 2. Operación inválida: Crear cliente sin nombre (Lanza MissingParameterError)
        try:
            c2 = self.add_client("", "invalid@example.com", "555-0101")
            results.append("2. SUCCESS: Invalid client created (Should not happen).")
        except Exception as e:
            results.append(f"2. CAUGHT EXPECTED ERROR (Invalid Client): {str(e)}")

        # 3. Operación válida: Crear servicio de sala válido
        try:
            s1 = RoomService("Conference Room A", 100.0, 20)
            self.add_service(s1)
            results.append("3. SUCCESS: Valid RoomService created.")
        except Exception as e:
            results.append(f"3. FAILED: {str(e)}")

        # 4. Operación inválida: Crear servicio con precio negativo (Lanza InvalidDataError)
        try:
            s2 = EquipmentService("Projector", -50.0, "Video")
            self.add_service(s2)
            results.append("4. SUCCESS: Invalid service created (Should not happen).")
        except Exception as e:
            results.append(f"4. CAUGHT EXPECTED ERROR (Invalid Service Price): {str(e)}")

        # 5. Operación válida: Crear servicio de consultoría
        try:
            s3 = ConsultingService("Tech Audit", 200.0, "Alice Smith")
            self.add_service(s3)
            results.append("5. SUCCESS: Valid ConsultingService created.")
        except Exception as e:
            results.append(f"5. FAILED: {str(e)}")

        # 6. Operación válida: Crear reserva válida
        try:
            r1 = self.create_reservation(c1, s1, 4) # 4 horas
            results.append("6. SUCCESS: Valid Reservation created.")
        except Exception as e:
            results.append(f"6. FAILED: {str(e)}")

        # 7. Operación válida: Confirmar reserva exitosamente (con impuestos)
        try:
            self.confirm_reservation(r1, apply_taxes=True)
            results.append(f"7. SUCCESS: Reservation confirmed. Total Cost: ${r1.total_cost:.2f}")
        except Exception as e:
            results.append(f"7. FAILED: {str(e)}")

        # 8. Operación inválida: Intentar confirmar una reserva ya confirmada (Lanza InvalidReservationError)
        try:
            self.confirm_reservation(r1)
            results.append("8. SUCCESS: Confirmed already confirmed reservation (Should not happen).")
        except Exception as e:
            results.append(f"8. CAUGHT EXPECTED ERROR (Double Confirmation): {str(e)}")

        # 9. Operación inválida: Reserva con servicio no disponible (Lanza ServiceUnavailableError)
        try:
            s1.is_available = False # Simulamos que el servicio se deshabilitó
            r2 = self.create_reservation(c1, s1, 2)
            self.confirm_reservation(r2)
            results.append("9. SUCCESS: Confirmed unavailable service (Should not happen).")
        except Exception as e:
            results.append(f"9. CAUGHT EXPECTED ERROR (Unavailable Service): {str(e)}")
        finally:
            s1.is_available = True # Restaurar disponibilidad para no afectar al sistema

        # 10. Operación inválida: Error de cálculo al crear reserva con duración negativa (Lanza InvalidDataError)
        try:
            r3 = self.create_reservation(c1, s3, -5)
            results.append("10. SUCCESS: Created reservation with negative duration (Should not happen).")
        except Exception as e:
            results.append(f"10. CAUGHT EXPECTED ERROR (Negative Duration): {str(e)}")

        self.logger.info("--- SIMULATION FINISHED ---")
        return results
