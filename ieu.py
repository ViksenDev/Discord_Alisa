from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/interactions', methods=['POST'])
def handle_interactions():
    data = request.json
    
    # Получение данных из запроса
    interaction_id = data['id']
    interaction_token = data['token']
    interaction_type = data['type']
    user_id = data['member']['user']['id']
    command_name = data['data']['name']
    
    # Обработка взаимодействия
    if interaction_type == 1:  # Взаимодействие Ping
        response_data = {
            'type': 1  # Ответ на взаимодействие
        }
    elif interaction_type == 2:  # Взаимодействие Command
        if command_name == 'hello':  # Пример команды "hello"
            response_data = {
                'type': 4,  # Ответ с эффектами (сообщение, эмоции и т. д.)
                'data': {
                    'content': f'Привет, <@{user_id}>!'
                }
            }
        else:
            response_data = {
                'type': 4,  # Ответ с эффектами
                'data': {
                    'content': 'Неизвестная команда. 😕'
                }
            }
    else:
        response_data = {
            'type': 4,  # Ответ с эффектами
            'data': {
                'content': 'Неизвестное взаимодействие. 😕'
            }
        }
    
    # Отправка ответа на взаимодействие
    response = jsonify(response_data)
    return response
    
if __name__ == '__main__':
    app.run()
