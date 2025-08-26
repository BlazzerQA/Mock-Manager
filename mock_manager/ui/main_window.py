import customtkinter as ctk
from ui.mocks_tab import MainTab
from ui.editor_tab import EditorTab
from ui.settings_tab import SettingsTab
from config import config_manager

class MockManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.title("Mock Manager")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height-50}+0+0")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0,weight=1)

         # Статус бар
        self.status_bar = ctk.CTkFrame(self,height=30, corner_radius=0, fg_color="#2c3e50")
        self.status_bar.grid(row=0,column=0,sticky="nsew",padx=0, pady=(20,0))

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text = "✅ Готов к работе",
            anchor = "w",
            font=("Arial",14),
            padx=10,
            text_color="#ecf0f1")
        self.status_label.pack(side="left", fill = "y")

        # Выбор окружения
        env_frame = ctk.CTkFrame(self.status_bar,fg_color="transparent")
        env_frame.pack(side="right",padx=(0,15))

        ctk.CTkLabel(env_frame, text="Окружение:").pack(side="left",fill="y", padx=(0,10))
        self.env_var = ctk.StringVar(value=config_manager.env)
        self.env_var.trace_add("write",self.on_env_changed)
        env_combo = ctk.CTkComboBox(
            env_frame, 
            values=list(config_manager.envs.keys()),
            variable=self.env_var,
            width=120,
            state="readonly"
            )
        env_combo.pack(side="right",fill="y", padx=(0,10))

        # Создаем контейнер для вкладок
        self.tab_frame = ctk.CTkFrame(self)
        self.tab_frame.grid(row=1,column=0,sticky="nsew",padx=0, pady=0)
        self.tab_frame.grid_rowconfigure(0, weight=1)
        self.tab_frame.grid_columnconfigure(0,weight=1)

        self.tab_view = ctk.CTkTabview(self.tab_frame)
        self.tab_view.grid(row=0,column=0,sticky="nsew",padx=10, pady=10)

        # Вкладки
        self.mocks_tab = MainTab(self.tab_view.add("Главная"),config_manager,self.update_status)
        self.editor_tab = EditorTab(self.tab_view.add("Редактор"),config_manager,self.update_status)
        self.settings_tab = SettingsTab(self.tab_view.add("Настройки"),config_manager,self.update_status)

        self.tab_view = self.tab_view

    def on_env_changed(self, *args):
        new_value = self.env_var.get()
        if new_value == self.env_var.get():
            print(f"Окружение изменено на: {new_value}")
            config_manager.env = new_value
            self.update_status("Смена окружения...")

    def update_status(self,message, status_type ="info"):
        colors = {
            "info": ("#C5F30E") ,     # Желтый: информационные сообщения
            "success": ("#27AE60"),   # Зеленый: успешные операции
            "error": ("#C0392B")      # Красный: ошибки
        }
        text_color = colors.get(status_type, colors["info"])

        self.status_label.configure(text=message,text_color=text_color)
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌"
        }
        icon = icons.get(status_type,["ℹ️"])
        self.status_label.configure(text=f"{icon} {message}")
