import requests, json
from config import config_manager

class MockService:
    def __init__(self):
       pass

    # Создать (POST)
    def create_mock(self,mock_data):
        try:
            # Путь запроса
            url = f"{config_manager.current_env_config['admin_url']}" + "/mocks"
            print(f"путь запроса {url}")
            # Заголовки запроса
            headers = {
                "Authorization": config_manager.token,
                "Content-Type": "application/json"
            }   
            # Тело запроса
            requestBody = mock_data
            print("Отправляемый payload:", json.dumps(requestBody, indent=4))
            response = requests.post(url, headers = headers, data = json.dumps(requestBody))

            if response.status_code == 200:
                return {
                    "success": True,
                    "mock_id": response.json().get("id")
                }
            else:
                return {
                    "success": False,
                    "error": f"{response.status_code}: {response.text}"
                }
        except Exception as e:
             return {
                    "success": False,
                    "error": str(e)
                }
            
    # Получить (GET)
    def load_mocks_gate(self,gate):
        try:
            # Путь запроса
            url = f"{config_manager.current_env_config['admin_url']}" + f"/mocks?gate={gate}"
            # Заголовки запроса"
            headers = {
                "Authorization": config_manager.token,
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers = headers)

            if response.status_code != 200:
                error_msg = f"Ошибка сервера: {response.status_code}"
                if response.text:
                    error_msg += f"- {response.text[:100]}..."
                return {"success": False, "error": error_msg}
            
            data = response.json()
            if 'data' not in data or not data['data']:
                return {"success":True,"data":[],"message":"Моки не найдены"}
            return {"success": True, "data": data['data']}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Ошибка сети: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Ошибка парсинга JSON: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Неизвестная ошибка: {str(e)}"}
        

    # Получить детальную информацию (GET)
    def get_mock_details(self,mock_id):
        try:
            # Путь запроса
            url = f"{config_manager.current_env_config['admin_url']}" + f"/mocks/{mock_id}"
            # Заголовки запроса"
            headers = {
                "Authorization": config_manager.token,
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers = headers)
            print(f"Код ответа: {response.status_code}")
            print(f"Тело ответа: {response.text}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    return data
                except ValueError:
                    error_msg = f"Ошибка парсинга JSON"
                    print(error_msg)
                    return {"success": False, "error": error_msg}
            else:
                error_msg = f"Ошибка сервера: {response.status_code}"
                return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Исключение при запросе: {str(e)}"
            return {"success": False, "error": error_msg}


    # Обновить (PUT)
    def update_mock(self,mock_id,mock_data):
        try:
            # Путь запроса
            url = f"{config_manager.current_env_config['admin_url']}" + f"/mocks/{mock_id}"
            # Заголовки запроса"
            headers = {
                "Authorization": config_manager.token,
                "Content-Type": "application/json"
            }
            # Тело запроса
            requestBody = mock_data
            print("Обновленный payload:", json.dumps(requestBody, indent=4))
            response = requests.put(url, headers = headers, data = json.dumps(requestBody))
            return response.status_code == 200
        except Exception as e:
            return False


    # Удалить (DELETE)
    def delete_mock(self, mock_id):
        try:
            # Путь запроса
            url = f"{config_manager.current_env_config['admin_url']}" + f"/mocks/{mock_id}"
            # Заголовки запроса
            headers = {
                "Authorization": config_manager.token,
                "Content-Type": "application/json"
            }
            response = requests.delete(url, headers = headers)
            print("Cтатус код:",response.status_code)
            return response.status_code == 200
        except Exception as e:
            return False
    

    

    

        
