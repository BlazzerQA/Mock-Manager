import customtkinter as ctk 
import tkinter as tk 
from tkinter import ttk, messagebox
import threading
from services.mock_service import MockService

class MainTab(ctk.CTkFrame):
    def __init__(self, parent, config, update_status):
        super().__init__(parent)
        self.config = config
        self.update_status = update_status
        self.mock_service = MockService()
        self.pack(fill="both", expand = True)
        self.build_ui()

    def build_ui(self):
    
        # Панель управления
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=10)

        # Выбор гейта
        ctk.CTkLabel(control_frame, text="GATE:").grid(row=0, column=0, padx=5, pady=5)
        self.gate_var = ctk.StringVar(value=self.config.gate)
        print(self.gate_var)
        self.gate_var.trace_add("write",self.on_gate_changed)
        env_combo = ctk.CTkComboBox(
            control_frame, 
            values=list(self.config.gates),
            variable=self.gate_var,
            width=160,
            state="readonly"
            )
        env_combo.grid(row=0, column=1, padx=5, pady=5)
        
        btn = ctk.CTkButton(control_frame, text="Загрузить", command = self.load_mocks_gate, width=100)
        btn.grid(row=0, column=2, padx=5, pady=5)
 
        # Фрейм для таблицы
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Создаем Treeview с прокруткой
        columns = ("gate", "method", "path", "description", "group", "id")
        self.mock_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings",
            selectmode="browse",
            style="Custom.Treeview")
        
        # Настройка колонок
        col_widths = [180, 150, 350, 500, 250, 400]
        col_headings = ["Гейт", "Метод", "Путь", "Описание", "Группа", "ID"]
        
        for col, width, heading in zip(columns, col_widths, col_headings):
            self.mock_tree.heading(col, text=heading)
            self.mock_tree.column(col, width=width, anchor="center")
        
        # Вертикальный скроллбар
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.mock_tree.yview)
        self.mock_tree.configure(yscrollcommand=vsb.set)
        
        # Горизонтальный скроллбар
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.mock_tree.xview)
        self.mock_tree.configure(xscrollcommand=hsb.set)
        
        # Размещение компонентов
        self.mock_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Настройка сетки
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Привязка события выбора
        self.mock_tree.bind("<<TreeviewSelect>>", self.on_mock_select)
        
        # Применяем стили
        self.style_treeview()

    def style_treeview(self):
        style = ttk.Style()
        
        # Общие настройки
        style.theme_use("default")
        style.configure("Custom.Treeview",
            background="#ffffff",
            foreground="#333333",
            rowheight=25,
            fieldbackground="#ffffff",
            borderwidth=0,
            font=("Segoe UI", 14)
        )
        style.configure("Custom.Treeview.Heading",
            background="#4a86e8",
            foreground="white",
            padding=5,
            font=("Segoe UI", 14, "bold")
        )
        style.map("Custom.Treeview",
            background=[('selected', '#4a86e8')],
            foreground=[('selected', 'white')]
        )
        
        # Для темной темы
        if ctk.get_appearance_mode() == "Dark":
            style.configure("Custom.Treeview",
                background="#2b2b2b",
                foreground="#e0e0e0",
                fieldbackground="#2b2b2b",
            )
            style.configure("Custom.Treeview.Heading",
                background="#1f6aa5",
                foreground="white",
            )
            style.map("Custom.Treeview",
                background=[('selected', '#1f6aa5')],
                foreground=[('selected', 'white')]
            )
    # Смена гейта
    def on_gate_changed(self, *args):
        new_value = self.gate_var.get()
        if new_value == self.gate_var.get():
            print(f"Гейт изменен на: {new_value}")
            self.config.gate = new_value
            self.update_status("Смена Гейта...")
    

    def on_mock_select(self, event):
        selected_item = self.mock_tree.selection()
        if selected_item:
            item_values = self.mock_tree.item(selected_item[0],'values')
            self.selected_mock_id = item_values[5]
            self.show_context_menu()

    # Получение моков (Загрузка данных)
    def load_mocks_gate(self):
        if not self.config.token:
            self.update_status("Ошибка: токен авторизации не установлен","error")
            return

        self.update_status("⏳ Загрузка моков...", "info")
        threading.Thread(target=self._load_mocks_gate_thread,daemon=True).start()

    def _load_mocks_gate_thread(self):
        gate = self.gate_var.get()
        result = self.mock_service.load_mocks_gate(gate)

        if result["success"]:
            if result.get("data"):
                self.after(0,self._populate_table,result["data"])
                count = len(result["data"])
                self.after(0,self.update_status, f"Загружено {count} моков","success")
            else:
                self.after(0, self.update_status, result.get("message", "ℹ️ Моки не найдены"), "info")
        else:
            self.after(0, self.update_status, f"❌ {result['error']}", "error")

    def get_mock_details(self,mock_id):
        try:
            result = self.mock_service.get_mock_details(mock_id)

            if result and "id" in result:
                self.selected_mock = result
                print(f"Текущий мок:{self.selected_mock}")
                self.after(0,self.open_editor_with_data, result)
            else:
                self.after(0,self.update_status,f"Не удалось получить данные для мока {mock_id}","error")
        except Exception as e:
            self.after(0,self.update_status,f"Ошибка получения данных: {str(e)}","error")


    def edit_mock(self):
        if hasattr(self,'selected_mock_id') and self.selected_mock_id:
            threading.Thread(target=self.get_mock_details,args=(self.selected_mock_id,),daemon=True).start()

    def delete_mock(self):
        if hasattr(self,'selected_mock_id') and self.selected_mock_id:
            confirm = messagebox.askyesno("Подтвердите удаление",f"Вы уверены, что ходите удалить мок {self.selected_mock_id}?")
            if confirm:
                threading.Thread(target=self._delete_mock_thread,args=(self.selected_mock_id,),daemon=True).start()
    
    def _delete_mock_thread(self,mock_id):
        try:
            success = self.mock_service.delete_mock(mock_id)
            if success:
                self.after(0, self.update_status("🗑 Мок успешно удален","success"))
                self.after(0,self.load_mocks_gate)
            else:
                 self.after(0, self.update_status("❌ Ошибка при удалении мока"))
        except ValueError as ve:
            self.after(0, self.update_status(f"⚠️ Ошибка валидации: {str(ve)}"))
        except Exception as e:
            self.after(0, self.update_status(f"⚠️ Неизвестная ошибка: {str(e)}"))



    def open_editor_with_data(self,mock_data):
         # Получаем главное окно
        main_window = self.winfo_toplevel()
        
        # Переключаемся на вкладку редактора
        main_window.tab_view.set("Редактор")
        
        # Заполняем данные в редакторе
        editor_tab = main_window.editor_tab
        editor_tab.load_mock_data(mock_data)

      

    # Отображение данных в таблице    
    def _populate_table(self,mocks_data):
        for item in self.mock_tree.get_children():
            self.mock_tree.delete(item)
        
        for mock in mocks_data:
            values = (
                mock.get('gate', ''),
                mock.get('httpMethod', ''),
                mock.get('requestPath', ''),
                mock.get('description', '') or '',
                mock.get('mockGroup', '') or '',
                mock.get('id','')
            )
            self.mock_tree.insert('','end',values=values)

    
    def show_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0,bg="#2b2b2b",fg="white")

        self.context_menu.configure(font=("Arial",12))

        self.context_menu.add_command(label="Редактировать",command=self.edit_mock)
        self.context_menu.add_command(label="Удалить",command=self.delete_mock)

        x=self.winfo_pointerx()
        y=self.winfo_pointery()

        self.context_menu.post(x,y)
        


        