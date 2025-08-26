import customtkinter as ctk
from PIL import Image
import threading
import time
import playsound 
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception as e:
        base_path = os.path.abspath(".")
    return os.path.join(base_path,relative_path)



class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent, config, update_status):
           super().__init__(parent,fg_color="transparent")
           self.config = config
           self.update_status = update_status
           self.pack(fill="both", expand = True)
           self.timer_runner = False
           self.build_ui()

    def build_ui(self):
    
        # Настройки авторизации
        auth_frame = ctk.CTkFrame(self,fg_color="transparent")
        auth_frame.pack(fill="x")
        
        ctk.CTkLabel(auth_frame, text="Авторизация", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        ctk.CTkLabel(auth_frame, text="Токен авторизации:").pack(anchor="w", padx=10, pady=(10, 0))
        self.token_var = ctk.StringVar()
        ctk.CTkEntry(auth_frame, textvariable = self.token_var).pack(fill="x", padx=10, pady=5)

        # Статус авторизации
        self.auth_status = ctk.CTkLabel(auth_frame, text="Не авторизован", fg_color="gray", corner_radius=5)
        self.auth_status.pack(side="top", fill="x", padx=10, pady=(10,0))

        ctk.CTkButton(auth_frame, text="Применить токен", command=self.apply_token).pack(pady=15)
        
        # Настройки внешнего вида
        theme_frame = ctk.CTkFrame(self,fg_color="transparent")
        theme_frame.pack(fill="x",pady=20)
        
        ctk.CTkLabel(theme_frame, text="Внешний вид", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        
        ctk.CTkLabel(theme_frame, text="Тема:").pack(anchor="w", padx=10, pady=(10, 0))
        self.theme_var = ctk.StringVar(value="System")
        theme_combo = ctk.CTkComboBox(theme_frame, variable=self.theme_var, values=["System", "Light", "Dark"])
        theme_combo.pack(fill="x", padx=10, pady=5)
        #theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # Информация о приложении
        info_frame = ctk.CTkFrame(self,fg_color="transparent")
        info_frame.pack(fill="x", padx=0, pady=20)
        
        ctk.CTkLabel(info_frame, text="О программе", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        ctk.CTkLabel(info_frame, text="Modern Mock Manager v1.0").pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(info_frame, text="Разработано для упрощения работы с моками").pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkButton(info_frame, text="☠️ Не нажимать!", command=self.start_timer, fg_color="black").pack(side="left", padx=10, pady=10)
        ctk.CTkButton(info_frame, text="Сообщить о проблеме", command=self.report_issue).pack(side="left", padx=10, pady=10)

    def start_timer(self):
        if not self.timer_runner:
            self.timer_runner = True
            threading.Thread(target=self.delayed_sound, daemon=True).start()
        else:
            print("Таймер уже запущен!")

    def delayed_sound(self):
        try:
            print("Таймер запущен! Через 60 сек. будет звук...")
            time.sleep(60)
            sound_path = resource_path("ui/black_stalker.mp3")
            if os.path.exists(sound_path):
                try:
                    playsound.playsound(sound_path)
                except Exception as e:
                    print(f"Ошибка воспроизведения: {e}")
            else:
                print(f"Файл не найден: {sound_path}")
        finally:
            self.timer_runner = False

    # Реализация авторизации с помощью токена 
    def apply_token(self):
        raw_token = self.token_var.get().strip()
        if not raw_token:
            self.update_status("Ошибка: токен пустой")
            return
        if not raw_token.lower().startswith("bearer"):
            raw_token = f"Bearer {raw_token}"
            self.config.token = raw_token
            self.update_status("Токен применён!")
            self.auth_status.configure(text="Авторизован", fg_color="green")
            print("Текущий токен:",self.config.token)


    def report_issue(self):
        image_window = ctk.CTkToplevel(self)
        image_window.title("Ответ от разраба:")
        image_window.geometry("600x400")
        image_window.attributes('-topmost',True)
        image_window.focus_force()

        def on_close():
           image_window.attributes('-topmost',False)
           image_window.destroy()
        
        image_window.protocol("WM_DELETE_WINDOW", on_close)

        try:
            image_path = resource_path("ui/image.jpg")
            img = Image.open(image_path)
            img.thumbnail((580,380))
            ctk_image = ctk.CTkImage(light_image=img,dark_image=img,size=img.size)
            image_label = ctk.CTkLabel(image_window,image = ctk_image,text="")
            image_label.pack(padx=10,pady=10)
        except Exception as e:
            error_label = ctk.CTkLabel(image_window,text=f"Не удалось загрузить ответ: {str(e)}",text_color="red")
            error_label.pack(padx=10,pady=10)
