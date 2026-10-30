document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('applicationForm');
    const successMessage = document.getElementById('form-success-message');

    // Твои настройки Telegram-бота и ID
    const BOT_TOKEN = '9010503321:AAEnipFj-yQImUYfoydV4LHEAjvqE1uphok';
    const CHAT_ID = '7935492851';

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();

            // Собираем данные из полей формы
            const fullname = document.getElementById('fullname').value;
            const phone = document.getElementById('phone').value;
            const email = document.getElementById('email').value;
            const direction = document.getElementById('direction').value;
            const about = document.getElementById('about-me').value;

            // Формируем сообщение с телефоном
            const text = `🚀 *Новая заявка в ByteForge!*\n\n` +
                         `👤 *ФИО:* ${fullname}\n` +
                         `📱 *Телефон:* ${phone}\n` +
                         `📧 *Email:* ${email}\n` +
                         `🎯 *Направление:* ${direction}\n` +
                         `📝 *О себе:* ${about || 'Не указано'}`;

            // Отправляем запрос через Telegram API
            fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: CHAT_ID,
                    text: text,
                    parse_mode: 'Markdown'
                })
            })
            .then(response => {
                if (response.ok) {
                    form.style.display = 'none';
                    if (successMessage) successMessage.style.display = 'block';
                    form.reset();
                } else {
                    alert('Ошибка при отправке. Проверь, запущен ли бот (@MrByteForge_bot).');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Ошибка соединения с сетью.');
            });
        });
    }
});