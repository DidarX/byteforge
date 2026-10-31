import html
import json
import os
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Все секреты берутся из переменных окружения (Render -> Environment)
TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ.get("CHAT_ID", "")              # куда приходят заявки с сайта
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")  # можно указать адрес сайта
URL = f'https://api.telegram.org/bot{TOKEN}/'

# максимальная длина полей заявки
MAX_FIELD = {"fullname": 100, "phone": 30, "email": 100, "direction": 100, "about": 1000}
_hits = {}


def too_many_requests(ip):
    """Не больше 5 заявок с одного IP за 10 минут."""
    now = time.time()
    hits = [t for t in _hits.get(ip, []) if now - t < 600]
    if len(hits) >= 5:
        _hits[ip] = hits
        return True
    hits.append(now)
    _hits[ip] = hits
    return False


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
        return True
    except Exception as e:
        print("Ошибка отправки:", e)
        return False


# ---------- Веб-сервер: пинг для Render + приём заявок с сайта ----------
class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "POST, GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _reply(self, code, body=b"ok", ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        self._reply(200)

    def do_HEAD(self):
        self._reply(200)

    def do_OPTIONS(self):
        self._reply(204, b"")

    def do_POST(self):
        if self.path != "/apply":
            return self._reply(404, b"not found")

        ip = (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()
        if too_many_requests(ip):
            return self._reply(429, b'{"ok":false}', "application/json")

        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > 10000:
                raise ValueError
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return self._reply(400, b'{"ok":false}', "application/json")

        f = {k: str(data.get(k, "")).strip()[:n] for k, n in MAX_FIELD.items()}
        if not (f["fullname"] and f["phone"] and f["email"]) or not CHAT_ID:
            return self._reply(400, b'{"ok":false}', "application/json")

        e = {k: html.escape(v) for k, v in f.items()}
        text = (
            "🚀 <b>Новая заявка в ByteForge!</b>\n\n"
            f"👤 <b>ФИО:</b> {e['fullname']}\n"
            f"📱 <b>Телефон:</b> {e['phone']}\n"
            f"📧 <b>Email:</b> {e['email']}\n"
            f"🎯 <b>Направление:</b> {e['direction'] or 'Не указано'}\n"
            f"📝 <b>О себе:</b> {e['about'] or 'Не указано'}"
        )

        if send_message(CHAT_ID, text):
            self._reply(200, b'{"ok":true}', "application/json")
        else:
            self._reply(502, b'{"ok":false}', "application/json")

    def log_message(self, *args):
        pass


def run_web():
    port = int(os.environ.get("PORT", 10000))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


# ---------- Команды бота ----------
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
    print("🤖 Бот ByteForge запущен и слушает сообщения...", flush=True)

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

                        print(f"Получено сообщение: {text} от {user_name}", flush=True)
                        handle_message(chat_id, text, user_name)
        except Exception as e:
            print("Ошибка соединения:", e, flush=True)
            time.sleep(5)


if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    check_updates()