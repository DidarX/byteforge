import json
import time
import urllib.request

TOKEN = '9010503321:AAEnipFj-yQImUYfoydV4LHEAjvqE1uphok'
URL = f'https://api.telegram.org/bot{TOKEN}/'

def send_message(chat_id, text):
    data = json.dumps({'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}).encode('utf-8')
    req = urllib.request.Request(URL + 'sendMessage', data=data, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print("Ошибка отправки:", e)

def check_updates():
    offset = 0
    print("🤖 Бот ByteForge запущен и слушает сообщения (без сторонних библиотек)...")
    
    while True:
        try:
            url = f"{URL}getUpdates?offset={offset}&timeout=30"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read().decode('utf-8'))
            
            if data['ok']:
                for update in data['result']:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update and 'text' in update['message']:
                        chat_id = update['message']['chat']['id']
                        text = update['message']['text']
                        user_name = update['message']['from'].get('first_name', 'Студент')
                        
                        print(f"Получено сообщение: {text} от {user_name}")
                        
                        if text.startswith('/start'):
                            msg = (
                                f"Привет, {user_name}! 👋\n\n"
                                "Я официальный бот студенческого клуба программирования **ByteForge** (МИТУ).\n"
                                "Используй меню или команды для связи с нами!"
                            )
                            send_message(chat_id, msg)
                            
                        elif text.startswith('/info'):
                            msg = (
                                "🚀 **О клубе ByteForge (МИТУ):**\n\n"
                                "Мы — сообщество студентов, создающее современные IT-проекты.\n"
                                "📌 **Направления:**\n"
                                "• Web Development\n"
                                "• Python & AI\n"
                                "• Robotics & IoT"
                            )
                            send_message(chat_id, msg)
                            
                        elif text.startswith('/contacts'):
                            msg = (
                                "📞 *Контакты организаторов:*\n\n"
                                "👤 Telegram: @fluxx\\_1418\n"
                                "📧 Email: support@byteforge.kz\n"
                                "📱 Телефон: +7 747 439 74 30"
                            )
                            send_message(chat_id, msg)
                        else:
                            send_message(chat_id, "Я понимаю команды /start, /info и /contacts. А заполнив заявку на сайте, ты передашь свои данные напрямую организаторам!")
        except Exception as e:
            print("Ошибка соединения:", e)
            time.sleep(5)

if __name__ == '__main__':
    check_updates()