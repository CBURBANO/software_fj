import tkinter as tk
from tkinter import ttk, messagebox
from manager import SystemManager
from models import RoomService, EquipmentService, ConsultingService
from exceptions import SystemErrorBase

class SoftwareFJApp:
    """
    Clase principal para la interfaz gráfica de usuario (GUI) usando Tkinter.
    Se encarga de mostrar los formularios y conectar con el SystemManager.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Management System")
        self.root.geometry("800x600")
        
        # Inicializamos el gestor del sistema (capa de lógica de negocio)
        self.manager = SystemManager()
        
        self.create_widgets()

    def create_widgets(self):
        """
        Crea los componentes visuales de la aplicación (Pestañas).
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab_clients = ttk.Frame(self.notebook)
        self.tab_services = ttk.Frame(self.notebook)
        self.tab_reservations = ttk.Frame(self.notebook)
        self.tab_simulation = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_clients, text="Clients")
        self.notebook.add(self.tab_services, text="Services")
        self.notebook.add(self.tab_reservations, text="Reservations")
        self.notebook.add(self.tab_simulation, text="Simulation & Logs")
        
        self.setup_clients_tab()
        self.setup_services_tab()
        self.setup_reservations_tab()
        self.setup_simulation_tab()

    # --- Pestaña Clientes ---
    def setup_clients_tab(self):
        """
        Configura la pestaña para la gestión de clientes.
        """
        frame_form = ttk.LabelFrame(self.tab_clients, text="Add Client")
        frame_form.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_form, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_client_name = ttk.Entry(frame_form)
        self.entry_client_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_client_email = ttk.Entry(frame_form)
        self.entry_client_email.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Phone:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_client_phone = ttk.Entry(frame_form)
        self.entry_client_phone.grid(row=2, column=1, padx=5, pady=5)
        
        btn_add = ttk.Button(frame_form, text="Add Client", command=self.add_client)
        btn_add.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.listbox_clients = tk.Listbox(self.tab_clients, height=15)
        self.listbox_clients.pack(fill='both', expand=True, padx=10, pady=10)

    def add_client(self):
        """
        Maneja el evento de agregar cliente, capturando excepciones si ocurren.
        """
        name = self.entry_client_name.get()
        email = self.entry_client_email.get()
        phone = self.entry_client_phone.get()
        
        try:
            client = self.manager.add_client(name, email, phone)
            self.listbox_clients.insert(tk.END, client.get_details())
            messagebox.showinfo("Success", "Client added successfully.")
            # Limpiar campos
            self.entry_client_name.delete(0, tk.END)
            self.entry_client_email.delete(0, tk.END)
            self.entry_client_phone.delete(0, tk.END)
            self.update_comboboxes()
        except SystemErrorBase as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

    # --- Pestaña Servicios ---
    def setup_services_tab(self):
        """
        Configura la pestaña para la gestión de servicios.
        """
        frame_form = ttk.LabelFrame(self.tab_services, text="Add Service")
        frame_form.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_form, text="Type:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_service_type = ttk.Combobox(frame_form, values=["Room", "Equipment", "Consulting"], state="readonly")
        self.combo_service_type.current(0)
        self.combo_service_type.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_service_name = ttk.Entry(frame_form)
        self.entry_service_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Base Price:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_service_price = ttk.Entry(frame_form)
        self.entry_service_price.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Specific Arg:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_service_arg = ttk.Entry(frame_form)
        self.entry_service_arg.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(frame_form, text="(Capacity/Equipment Type/Consultant Name)").grid(row=3, column=2, padx=5, pady=5)
        
        btn_add = ttk.Button(frame_form, text="Add Service", command=self.add_service)
        btn_add.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.listbox_services = tk.Listbox(self.tab_services, height=15)
        self.listbox_services.pack(fill='both', expand=True, padx=10, pady=10)

    def add_service(self):
        """
        Maneja el evento de agregar servicio.
        """
        svc_type = self.combo_service_type.get()
        name = self.entry_service_name.get()
        
        try:
            price = float(self.entry_service_price.get())
        except ValueError:
            messagebox.showerror("Error", "Base price must be a numeric value.")
            return
            
        arg = self.entry_service_arg.get()
        
        try:
            if svc_type == "Room":
                try:
                    capacity = int(arg)
                except ValueError:
                    raise SystemErrorBase("Capacity must be an integer.")
                service = RoomService(name, price, capacity)
            elif svc_type == "Equipment":
                service = EquipmentService(name, price, arg)
            else:
                service = ConsultingService(name, price, arg)
                
            self.manager.add_service(service)
            self.listbox_services.insert(tk.END, service.get_details())
            messagebox.showinfo("Success", f"{svc_type} Service added successfully.")
            self.update_comboboxes()
            
            # Limpiar campos
            self.entry_service_name.delete(0, tk.END)
            self.entry_service_price.delete(0, tk.END)
            self.entry_service_arg.delete(0, tk.END)
        except SystemErrorBase as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))

    # --- Pestaña Reservas ---
    def setup_reservations_tab(self):
        """
        Configura la pestaña para la gestión de reservas.
        """
        frame_form = ttk.LabelFrame(self.tab_reservations, text="Create Reservation")
        frame_form.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_form, text="Client:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_res_client = ttk.Combobox(frame_form, state="readonly", width=40)
        self.combo_res_client.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Service:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_res_service = ttk.Combobox(frame_form, state="readonly", width=40)
        self.combo_res_service.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Duration (hrs/days/sessions):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_res_duration = ttk.Entry(frame_form)
        self.entry_res_duration.grid(row=2, column=1, padx=5, pady=5)
        
        btn_add = ttk.Button(frame_form, text="Create Reservation", command=self.create_reservation)
        btn_add.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.listbox_reservations = tk.Listbox(self.tab_reservations, height=10)
        self.listbox_reservations.pack(fill='both', expand=True, padx=10, pady=5)
        
        btn_confirm = ttk.Button(self.tab_reservations, text="Confirm Selected Reservation", command=self.confirm_reservation)
        btn_confirm.pack(pady=5)

    def update_comboboxes(self):
        """
        Actualiza los valores de los combobox cuando se agregan clientes o servicios.
        """
        self.combo_res_client['values'] = [c.name for c in self.manager.clients]
        self.combo_res_service['values'] = [s.name for s in self.manager.services]

    def create_reservation(self):
        """
        Maneja la creación de una reserva en estado Pendiente.
        """
        idx_client = self.combo_res_client.current()
        idx_service = self.combo_res_service.current()
        
        if idx_client < 0 or idx_service < 0:
            messagebox.showwarning("Warning", "Please select a client and a service.")
            return
            
        client = self.manager.clients[idx_client]
        service = self.manager.services[idx_service]
        
        try:
            duration = float(self.entry_res_duration.get())
        except ValueError:
            messagebox.showerror("Error", "Duration must be a numeric value.")
            return
            
        try:
            res = self.manager.create_reservation(client, service, duration)
            self.refresh_reservations_list()
            messagebox.showinfo("Success", "Reservation created successfully.")
            self.entry_res_duration.delete(0, tk.END)
        except SystemErrorBase as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def confirm_reservation(self):
        """
        Maneja la confirmación de la reserva seleccionada en el Listbox.
        Muestra en pantalla errores de validación y de lógica de negocio usando try/except.
        """
        sel = self.listbox_reservations.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Select a reservation to confirm.")
            return
            
        idx = sel[0]
        reservation = self.manager.reservations[idx]
        
        try:
            # Confirmamos sin parámetros adicionales (se usarán los por defecto definidos en los modelos)
            self.manager.confirm_reservation(reservation)
            self.refresh_reservations_list()
            messagebox.showinfo("Success", f"Reservation confirmed successfully!\nTotal Cost: ${reservation.total_cost:.2f}")
        except SystemErrorBase as e:
            messagebox.showerror("Confirmation Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))

    def refresh_reservations_list(self):
        """
        Refresca el Listbox de reservas leyendo desde el SystemManager.
        """
        self.listbox_reservations.delete(0, tk.END)
        for r in self.manager.reservations:
            self.listbox_reservations.insert(tk.END, r.get_details())

    # --- Pestaña Simulación ---
    def setup_simulation_tab(self):
        """
        Configura la pestaña de simulación de operaciones exigida en los requerimientos.
        """
        btn_sim = ttk.Button(self.tab_simulation, text="Run 10 Operations Simulation", command=self.run_simulation)
        btn_sim.pack(pady=10)
        
        self.text_sim = tk.Text(self.tab_simulation, height=25, state='disabled')
        self.text_sim.pack(fill='both', expand=True, padx=10, pady=10)

    def run_simulation(self):
        """
        Ejecuta la simulación de 10 operaciones y muestra los resultados en el cuadro de texto.
        También actualiza las listas de la interfaz gráfica con los datos simulados válidos.
        """
        results = self.manager.run_simulation()
        
        self.text_sim.config(state='normal')
        self.text_sim.delete('1.0', tk.END)
        for res in results:
            self.text_sim.insert(tk.END, res + "\n\n")
        self.text_sim.config(state='disabled')
        
        # Refrescar listas visuales en caso de que la simulación haya agregado datos exitosos
        self.listbox_clients.delete(0, tk.END)
        for c in self.manager.clients:
            self.listbox_clients.insert(tk.END, c.get_details())
            
        self.listbox_services.delete(0, tk.END)
        for s in self.manager.services:
            self.listbox_services.insert(tk.END, s.get_details())
            
        self.refresh_reservations_list()
        self.update_comboboxes()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoftwareFJApp(root)
    root.mainloop()
