# pip install 
#   requests       # HTTP-запросы 
#   pytest         # фреймворк для тестов 
#   pytest-html    # HTML-отчеты 
#   python-dotenv  # управление секретами 
#   jsonschema     # валидация JSON-структур
#   Faker          # генерация тестовых данных

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import urllib3
from requests.adapters import HTTPAdapter

import uuid
import json
from datetime import datetime

# Отключаем предупреждения о недоверенных сертификатах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Создаем кастомную сессию с повторами запросов
def create_session():
    session = requests.Session()
    
    # # Настраиваем политику повторов
    # retry_strategy = Retry(
    #     total=3,
    #     backoff_factor=0.3,
    #     status_forcelist=[429, 500, 502, 503, 504],
    #     allowed_methods=["POST", "GET"]
    # )
    
    # adapter = HTTPAdapter(max_retries=retry_strategy)
    # session.mount("https://", adapter)
    
    return session

class APITesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("API Tester")
        self.root.geometry("700x500")
        
        # Переменные
        self.api_host = tk.StringVar(value="https://mp40-gateway.mp40-uat-static.k8s-dev.gksm.local/mobileapi")
        self.device_os = tk.StringVar(value="ios")
        self.product_id = tk.StringVar(value="21292640299")
        
        # Создание интерфейса
        self.create_widgets()
    
    def create_widgets(self):
        # Фрейм настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Поля ввода
        ttk.Label(settings_frame, text="API Host:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.api_host, width=60).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(settings_frame, text="Device OS:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        os_combo = ttk.Combobox(settings_frame, textvariable=self.device_os, width=10, state="readonly")
        os_combo['values'] = ('ios', 'android')
        os_combo.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(settings_frame, text="Product ID:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.product_id, width=20).grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Кнопки
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Запустить тест", command=self.run_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить логи", command=self.save_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Выход", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Лог
        log_frame = ttk.LabelFrame(self.root, text="Результаты")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled', height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе...")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_msg = f"[{timestamp}] {message}\n"
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, formatted_msg)
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)
        self.root.update()
    
    def get_auth_token(self):
        device_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())

        headers = {
            'x-real-ip': '45.138.156.138',
            'user-agent': 'android-4.81.0-dev-google',
            'locale': 'ru',
            'country': 'RU',
            'X-Request-Id': request_id,
            'city-id': '1720920299',
            'x-user-id': '123',
            'device-id': device_id,
            'eutc': 'UTC+3',
            'Content-Type': 'application/json'
        }
        
        data = {"device": {"id": device_id, "os": self.device_os.get()}}
        
        try:
            response = requests.post(
                f"{self.api_host.get()}/api/v1/auth/anonym",
                headers=headers,
                json=data,
                timeout=10,
                verify= False
            )
            response.raise_for_status()
            response_data = response.json()
            return response_data['data']['token']['accessToken'], response_data['data']['profile']['id']
        except Exception as e:
            self.log_message(f"❌ Ошибка аутентификации: {str(e)}")
            return None, None
    
    def get_product_info(self, access_token, profile_id):
        request_id = str(uuid.uuid4())
        installation_id = str(uuid.uuid4())
        
        headers = {
            'Authorization': f'{access_token}',
            'User-Agent': 'android-4.81.0-dev-google',
            'country': 'RU',
            'X-Request-Id': request_id,
            'locale': 'ru',
            'city-id': '32220299',
            'Content-Type': 'application/json',
            'X-Pers-Tags': 'summary_on,highlights_on',
            'eutc': '',
            'installation-id': installation_id,
            'x-user-id': profile_id
        }
        
        try:
            response = requests.post(
                f"{self.api_host.get()}/api/v2/products/{self.product_id.get()}",
                headers=headers,
                timeout=10,
                verify=False
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log_message(f"❌ Ошибка получения продукта: {str(e)}")
            return None
    
    def run_test(self):
        self.log_message("🚀 Начинаем тестирование API...")
        self.status_var.set("Аутентификация...")
        
        # Шаг 1: Аутентификация
        self.log_message("🔐 Отправка запроса аутентификации...")
        access_token, profile_id = self.get_auth_token()
        
        if access_token:
            self.log_message("✅ Успешная аутентификация!")
            self.log_message(f"    Access Token: {access_token[:50]}...")
            self.log_message(f"    Profile ID: {profile_id}")
            self.status_var.set("Получение данных продукта...")
            
            # Шаг 2: Получение информации о продукте
            self.log_message(f"📦 Запрос информации о продукте {self.product_id.get()}...")
            product_info = self.get_product_info(access_token, profile_id)
            
            if product_info:
                self.log_message("✅ Данные продукта получены!")
                if 'data' in product_info and 'product' in product_info['data']:
                    product_data = product_info['data']['product']
                    self.log_message(f"    Название: {product_data.get('name', 'N/A')}")
                    
                    if 'price' in product_data:
                        price = product_data['price']['catalog']
                        self.log_message(f"    Цена: {price.get('value', 'N/A')} {price.get('currency', '')}")
                    
                    if 'skus' in product_data and isinstance(product_data['skus'], list) and len(product_data['skus']) > 0:
                        first_sku = product_data['skus'][0]
                        is_replenishment = first_sku.get('isReplenishment', False)
                        in_skus = "Да" if is_replenishment else "Нет"
                        self.log_message(f"     Возможность пополнения: {in_skus}")
                
                self.log_message("🎉 Тестирование завершено успешно!")
                self.status_var.set("Тестирование завершено успешно!")
        
    def save_logs(self):
        log_text = self.log_area.get("1.0", tk.END)
        if log_text.strip():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_test_log_{timestamp}.txt"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_text)
                messagebox.showinfo("Успех", f"Логи сохранены в файл: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить логи: {str(e)}")
        else:
            messagebox.showwarning("Пустой лог", "Нет данных для сохранения")

if __name__ == "__main__":
    root = tk.Tk()
    app = APITesterApp(root)
    root.mainloop()