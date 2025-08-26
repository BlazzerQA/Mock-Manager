import customtkinter as ctk 
from tkinter import scrolledtext
import json
from services.mock_service import MockService
from services.json_service import JsonService

class EditorTab(ctk.CTkFrame):
    def __init__(self, parent, config, update_status):
        super().__init__(parent)
        self.config = config
        self.update_status = update_status
        self.mock_service = MockService()
        self.json_service = JsonService()
        self.pack(fill="both",expand = True)
        self.build_ui()

    def build_ui (self):
        print("началась сборка ui..")
        # Основной контейнер с разделением на две части
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)
            
        # Левая панель - параметры
        left_frame = ctk.CTkFrame(main_frame, width=400)
        left_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)
        
        # Параметры
        params_frame = ctk.CTkScrollableFrame(left_frame)
        params_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
        fields = [
            ("enabled", "Включен", "check"),
            ("gate", "Гейт", "combo", ["PRODUCT_GATE", "CONTENT_GATE", "USER_GATE", "CMS_GATE"]),
            ("httpMethod", "HTTP метод", "combo", ["GET", "POST", "PUT", "DELETE"]),
            ("requestPath", "Путь запроса", "entry"),
            ("responseStatus", "Статус ответа", "combo", ["200","404","500"]),
            ("priority", "Приоритет", "entry"),
            ("description", "Описание", "entry"),
            ("mockGroup", "Группа моков", "entry"),
        ]
            
        self.mock_vars = {}
        for field, label, field_type, *options in fields:
            frame = ctk.CTkFrame(params_frame)
            frame.pack(fill="x", pady=5)
                
            ctk.CTkLabel(frame, text=label + ":", width=120).pack(side="left", padx=5)
                
            if field_type == "entry":
                var = ctk.StringVar()
                entry = ctk.CTkEntry(frame, textvariable=var)
                entry.pack(fill="x", expand=True, padx=5)
                self.mock_vars[field] = var
                    
            elif field_type == "combo":
                var = ctk.StringVar()
                combo = ctk.CTkComboBox(frame, variable=var, values=options[0])
                combo.pack(fill="x", expand=True, padx=5)
                self.mock_vars[field] = var
                    
            elif field_type == "check":
                var = ctk.BooleanVar(value=True)
                check = ctk.CTkCheckBox(frame, text="", variable=var)
                check.pack(side="left", padx=5)
                self.mock_vars[field] = var

        frame_id = ctk.CTkFrame(params_frame)
        frame_id.pack(fill="x", expand=True, padx=10, pady=100)
        ctk.CTkLabel(frame_id, text="ID мока:", width=120).pack(side = "left", padx=5)
        self.mock_id_var = ctk.StringVar(value=getattr(self,"mock_id", ""))
        id_entry = ctk.CTkEntry(frame_id, textvariable = self.mock_id_var)
        id_entry.pack(fill = "x", expand = True, padx = 5)
            

        # Кнопки в левой панели
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="✅ Создать мок", command = self.create_mock).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="♻️ Обновить мок", command = self.update_mock).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="⚠️ Удалить мок", command = self.delete_mock, fg_color="#8F0909").pack(side="left", padx=5)
            
        # Правая панель - тело ответа
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, pady=10)

        # Заголовок
        header_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx = 10, pady =(10,5))
        ctk.CTkLabel(header_frame, text="Тело ответа:").pack(side="left")

        # Кнопки для тела ответа
        button_frame = ctk.CTkFrame(header_frame,fg_color="transparent")
        button_frame.pack(side="right")
        btn_settings = {"width":100,"height":28,"font":("",12),"corner_radius":6}
        ctk.CTkButton(button_frame, text="Очистить", command=self.clear_response,**btn_settings).pack(side="right", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="Проверить", command=self.validate_json,**btn_settings).pack(side="right", padx=5, pady=0)
        ctk.CTkButton(button_frame, text="Форматировать", command=self.format_json,**btn_settings).pack(side="right", padx=5, pady=0)
       
        # Тело ответа
        self.response_body = scrolledtext.ScrolledText(
            right_frame,
            wrap="word",
            font=("Consolas", 16),
            bg ="#1e1e1e",
            fg ="#d4d4d4",
            insertbackground ="white",
            undo=True)
        self.response_body.pack(fill="both", expand=True, padx=10, pady=(0, 10)) 
        self.response_body.tag_configure("error",background = "#710707")
        # Обработчики событий
        self.response_body.bind("<Control-V>", self.on_paste)
        self.response_body.bind("<Control-v>", self.on_paste)
        self.response_body.bind("<<Paste>>", self.on_paste)

            
    def on_paste(self, event=None):
        try:
            clipboard_text = self.clipboard_get()
            try:
                parsed_json = json.loads(clipboard_text)
                formatted_json = json.dumps(parsed_json, indent=4,ensure_ascii=False)
                if self.response_body.tag_ranges("sel"):
                    self.response_body.delete("sel.first","sel.last")
                self.response_body.insert("insert",formatted_json)
                self.json_service.hightlight_json(self.response_body)
            except json.JSONDecodeError:
                if self.response_body.tag_ranges("sel"):
                    self.response_body.delete("sel.first","sel.last")
                self.response_body.insert("insert",clipboard_text)
        except Exception as e:
            if self.response_body.tag_ranges("sel"):
                self.response_body.delete("sel.first","sel.last")
            self.response_body.insert("insert",clipboard_text)
        return "break"
        
    def format_json(self):
        try:
            raw_text = self.response_body.get("1.0", "end-1c").strip() 
            parsed = json.loads(raw_text)
            formatted = json.dumps(parsed, indent=4,ensure_ascii=False)
            self.response_body.delete("1.0","end")
            self.response_body.insert("1.0",formatted)
            self.json_service.hightlight_json(self.response_body)
            self.update_status("JSON отформатирован","success")
        except Exception as e:
            self.update_status(f"Ошибка форматирования {str(e)}","error")

    def validate_json(self):
        try:
            raw_text = self.response_body.get("1.0", "end-1c")
            parsed = json.loads(raw_text)
            self.response_body.tag_remove("error","1.0","end")
            self.update_status("JSON валиден","success")
            return True
        except Exception as e:
            content =  self.response_body.get("1.0","end-1c")
            error_line = 1
            error_char = 0
            
            for i, char in enumerate(content):
                if i >= e.pos:
                    break
                if char == '\n':
                    error_line +=1
                    error_char = 0
                else:
                    error_char +=1
            start_pos = f"{error_line}.0"
            end_pos = f"{error_line}.end"
            self.response_body.tag_add("error",start_pos,end_pos)
            self.update_status(f"Ошибка в JSON! {str(e)}","error")   

    def clear_response(self):
        self.response_body.delete("1.0","end")
        self.update_status("Очищено!","info")


    # Получить
    def load_mock_data(self,mock_data):
        #self.clear_all_fields()

        for field,var in self.mock_vars.items():
            if field in mock_data:
                value = mock_data[field]
                if isinstance(var,ctk.BooleanVar):
                    var.set(bool(value))
                elif isinstance(var,ctk.StringVar):
                    var.set(str(value))

        if 'id' in mock_data:
            self.mock_id_var.set(str(mock_data['id']))
        
        response_body = mock_data.get("responseBody","{}")
        if isinstance(response_body,str):
            try:
                prepared_json=self.json_service.prepare_json(response_body)
                formatted_json = json.dumps(json.loads(prepared_json),indent=4,ensure_ascii=False)
                response_body = formatted_json
            except(ValueError,  json.JSONDecodeError):
                pass
        self.response_body.delete("1.0","end")
        self.response_body.insert("1.0",response_body)
        self.json_service.hightlight_json(self.response_body)
        self.update_status(f"Загружен мок: {mock_data['id']}","success")
   
    # Создать
    def create_mock(self):
        try:
            raw_text = self.response_body.get("1.0", "end-1c").strip() 
            prepared_json = self.json_service.prepare_json(raw_text)

            mock_data = {
            "enabled": self.mock_vars["enabled"].get(),
            "gate": self.mock_vars["gate"].get(),
            "httpMethod": self.mock_vars["httpMethod"].get(),
            "requestPath": self.mock_vars["requestPath"].get(),
            "condition": "true",
            "responseBody": prepared_json,
            "responseStatus": int(self.mock_vars["responseStatus"].get()),
            "priority": int(self.mock_vars["priority"].get()),
            "description": self.mock_vars["description"].get(),
            "ttl": None,
            "mockGroup": self.mock_vars["mockGroup"].get(),
             }
            result = self.mock_service.create_mock(mock_data)
            
            if result["success"]:
                self.mock_id_var.set(result["mock_id"])
                self.update_status("✅ Мок успешно создан")
            else:
                self.update_status(f"❌ Ошибка: {result["error"]}")
                print(result["error"])
        except ValueError as ve:
            self.update_status(f"⚠️ Ошибка валидации: {str(ve)}")
        except Exception as e:
            self.update_status(f"⚠️ Неизвестная ошибка: {str(e)}")

    # Обновить
    def update_mock(self):
        mock_id = self.mock_id_var.get().strip()
        if not mock_id:
            self.update_status("Введите ID мока для обновления","success")
            return
        try:
            raw_text = self.response_body.get("1.0", "end-1c").strip() 
            prepared_json = self.json_service.prepare_json(raw_text)

            mock_data = {
            "enabled": self.mock_vars["enabled"].get(),
            "gate": self.mock_vars["gate"].get(),
            "httpMethod": self.mock_vars["httpMethod"].get(),
            "requestPath": self.mock_vars["requestPath"].get(),
            "condition": "true",
            "responseBody": prepared_json,
            "responseStatus": int(self.mock_vars["responseStatus"].get()),
            "priority": int(self.mock_vars["priority"].get()),
            "description": self.mock_vars["description"].get(),
            "ttl": None,
            "mockGroup": self.mock_vars["mockGroup"].get(),
             }
            success = self.mock_service.update_mock(mock_id, mock_data)

            if success:
                self.update_status("♻️ Мок успешно обновлен")
            else:
                self.update_status("❌ Ошибка при обновлении мока")
        except ValueError as ve:
            self.update_status(f"⚠️ Ошибка валидации: {str(ve)}")
        except Exception as e:
            self.update_status(f"⚠️ Неизвестная ошибка: {str(e)}")


    # Удалить
    def delete_mock(self):
        mock_id = self.mock_id_var.get().strip()
        if not mock_id:
            self.update_status("Введите ID мока для удален", "error")
            return
        try:
            success = self.mock_service.delete_mock(mock_id)
            if success:
                self.mock_id_var.set("")
                self.update_status("🗑 Мок успешно удален")
            else:
                self.update_status("❌ Ошибка при удалении мока")
        except ValueError as ve:
            self.update_status(f"⚠️ Ошибка валидации: {str(ve)}")
        except Exception as e:
            self.update_status(f"⚠️ Неизвестная ошибка: {str(e)}")




