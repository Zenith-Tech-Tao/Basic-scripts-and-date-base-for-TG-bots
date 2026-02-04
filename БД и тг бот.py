import telebot
import sqlite3
from config import TOKEN


bot = telebot.TeleBot(TOKEN)

# ===================================БАЗА ДАННЫХ====================================
# Создаём соединение с базой данных и разрешаем его использование из разных потоков,
# По умолчанию, без этого параметра, соединение можно использовать только в том же потоке, где оно было создано.
# Все из-за того что Telebot работает асинхронно
dp = sqlite3.connect('DP_TG_BOT_one.dp', check_same_thread=False)

cursor = dp.cursor()


#cursor.execute("DROP TABLE IF EXISTS base_tg_bot_zametka")


cursor.execute('''CREATE TABLE IF NOT EXISTS base_tg_bot_zametka (                 

id INTEGER PRIMARY KEY AUTOINCREMENT,
user INTEGER,
text TEXT,
data TEXT DEFAULT (DATETIME('now','localtime'))

)
''')
dp.commit()

# ====================================================================================


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Приветствуем вас в боте по записям заметок")
    bot.send_message(message.chat.id,"Введите команду '/go'")

@bot.message_handler(commands=['go'])
def go(message):
    bot.send_message(message.chat.id,  "Напишите что нужно записать в заметки:")
    bot.register_next_step_handler(message, save)

def save(message):
    user = message.from_user.id # Получаем id или юз пользователя, который отправил сообщение
    text = message.text.strip() #  Получаем текст сообщения и удаляем начальные и конечные пробелы для чистоты
    # strip() Удаляет все начальные и конечные пробелы из текста, чтобы избавиться от лишних пробелов в начале и конце строки

    if text:
        cursor.execute("INSERT INTO base_tg_bot_zametka (user, text) VALUES (?,?)",
                       (user,text))
        dp.commit()
        bot.reply_to(message,"✅ Заметка сохранена!")
    else:
        bot.reply_to(message, "Пожалуйста, напишите что нужно сохранить.")

@bot.message_handler(commands=['see'])
def see(message):
    cursor.execute("SELECT text, data FROM base_tg_bot_zametka WHERE user = ?",
                   (message.from_user.id,))
    user_see = cursor.fetchall()

    if user_see:
        info = "Ваши заметки:\n"
        for note_text, note_date in user_see:



            date_part, time_part = note_date.split(' ')

            year, month, day = date_part.split('-')

            hours_minut = time_part[:5]

            otvet_data_time = f"{day}.{month}.{year} {hours_minut}"


            info += f"\n• {note_text}\n{otvet_data_time}\n\n"

    else:

        info = "📭 У вас нет сохраненных заметок"

    bot.reply_to(message, info)  # Вывод инфы



@bot.message_handler(commands=['menu'])
def menu(message):
    bot.send_message(message.chat.id, "Список команд:\n"
                                      "/start - Рестарт\n"
                                      "/go - Записать заметку\n"
                                      "/see - Посмотреть все свои заметки")


bot.polling()