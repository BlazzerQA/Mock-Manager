import json
import re

class JsonService:
    @staticmethod
    def prepare_json(raw_text):
        if not raw_text.strip():
            raise ValueError("Тело ответа пустое!")
        try:
            parsed = json.loads(raw_text)
            return json.dumps(parsed, separators=(',' , ':'),ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка в формате JSON: {str(e)}")
        

    @staticmethod
    def hightlight_json(text_widget):
        text_widget.tag_remove("error","1.0","end")
        try:
            content = text_widget.get("1.0", "end-1c")
            json.loads(content)
            for tag in ["key","string","number","boolean","null"]:
                text_widget.tag_remove(tag, "1.0","end")

            #Цвет тегов
            text_widget.tag_configure("key", foreground = "#4BA8FE")
            #text_widget.tag_configure("string", foreground = "#CDCDCD")
            text_widget.tag_configure("number", foreground = "#14B12C")
            text_widget.tag_configure("boolean", foreground = "#FF0000")
            text_widget.tag_configure("null", foreground = "#FFFFFF")

            #Подсветка ключей
            for match in re.finditer(r'\"(.*?)\"\s*:', content):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()-1} chars"
                text_widget.tag_add("key", start, end)
            # #Подсветка строк
            # for match in re.finditer(r'(?<!:)\s*"([^"]*?)"', content):
            #     start = f"1.0 + {match.start()} chars"
            #     end = f"1.0 + {match.end()} chars"
            #     text_widget.tag_add("string", start, end)
            #Подсветка чисел
            for match in re.finditer(r'\b\d+(\.\d+)?\b', content):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                text_widget.tag_add("number", start, end)
            #Подсветка boolean
            for match in re.finditer(r'\btrue\b|\bfalse\b', content):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                text_widget.tag_add("boolean", start, end)
            #Подсветка null
            for match in re.finditer(r'\bnull\b', content):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                text_widget.tag_add("null", start, end)
            return True
        except json.JSONDecodeError as e:
            return False
