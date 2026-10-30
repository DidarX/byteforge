import html
import json
import os
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

# Токен берётся из переменной окружения BOT_TOKEN (задаётся в настройках хостинга)
TOKEN = os.environ["BOT_TOKEN"]
URL = f'https://api.telegram.org/bot{TOKEN}/'


# ---------- Мини-сервер: чтобы Render видел открытый порт ----------
class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


def run_web():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Ping).serve_forever()


# ---------- Telegram ----------
def send_message(chat_id, text):
    data = json.dumps({
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
    }).encode('utf-8')
    req = urllib.request.Request(
        URL + 'sendMessage',
        data=data,
        headers={'Content-Type': 'application/json'},
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print("Ошибка отправки:", e)


def handle_message(chat_id, text, user_name):
    name = html.escape(user_name)

    if text.startswith('/start'):
        msg = (
            f"Привет, {name}! 👋\n\n"
            "Я официальный бот студенческого клуба программирования <b>ByteForge</b> (МИТУ).\n"
            "Используй меню или команды для связи с нами!"
        )
    elif text.startswith('/info'):
        msg = (
            "🚀 <b>О клубе ByteForge (МИТУ):</b>\n\n"
            "Мы — сообщество студентов, создающее современные IT-проекты.\n"
            "📌 <b>Направления:</b>\n"
            "• Web Development\n"
            "• Python &amp; AI\n"
            "• Robotics &amp; IoT"
        )
    elif text.startswith('/contacts'):
        msg = (
            "📞 <b>Контакты организаторов:</b>\n\n"
            "👤 Telegram: @fluxx_1418\n"
            "📧 Email: support@byteforge.kz\n"
            "📱 Телефон: +7 747 439 74 30"
        )
    else:
        msg = (
            "Я понимаю команды /start, /info и /contacts. "
            "А заполнив заявку на сайте, ты передашь свои данные напрямую организаторам!"
        )

    send_message(chat_id, msg)


def check_updates():
    offset = 0
    print("🤖 Бот ByteForge запущен и слушает сообщения...")

    while True:
        try:
            url = f"{URL}getUpdates?offset={offset}&timeout=30"
            response = urllib.request.urlopen(url, timeout=40)
            data = json.loads(response.read().decode('utf-8'))

            if data['ok']:
                for update in data['result']:
                    offset = update['update_id'] + 1

                    message = update.get('message')
                    if message and 'text' in message:
                        chat_id = message['chat']['id']
                        text = message['text']
                        user_name = message.get('from', {}).get('first_name', 'Студент')

                        print(f"Получено сообщение: {text} от {user_name}")
                        handle_message(chat_id, text, user_name)
        except Exception as e:
            print("Ошибка соединения:", e)
            time.sleep(5)


if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    check_updates()
