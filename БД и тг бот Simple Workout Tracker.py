import telebot
import sqlite3
from config import TOKEN
from telebot import types
from datetime import datetime

bot = telebot.TeleBot(TOKEN)

# ===================================БАЗА ДАННЫХ====================================

dp = sqlite3.connect('DP_TG_BOT_two.dp',check_same_thread=False)

cursor = dp.cursor()


#cursor.execute("DROP TABLE IF EXISTS workout")


cursor.execute("""CREATE TABLE IF NOT EXISTS workout (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
name TEXT,
training TEXT,
start_time TEXT,
end_time TEXT,
minutes REAL,
workout_date TEXT DEFAULT (DATETIME('now', 'localtime'))
)
""")

dp.commit()



# ===================================КОМАНДЫ====================================

'''@bot.message_handler(commands=['start'])
def start(message):

    markup = types.InlineKeyboardMarkup()
    btn1_start = types.InlineKeyboardButton('Начать', callback_data = 'start')
    btn2_end = types.InlineKeyboardButton('Закончить',  callback_data = 'end')
    btn3_stats = types.InlineKeyboardButton('История', callback_data = 'history')

    markup.row(btn1_start,btn2_end)
    markup.row(btn3_stats)

    bot.send_message(message.chat.id, "🏋️ Simple Workout Tracker\n\n"
                                      "Привет! Я твой личный помощник для отслеживания тренировок. "
                                      "Я помогу тебе фиксировать прогресс и следить за временем в зале.\n\n"
                                      "Выберите действие на панели ниже:", reply_markup=markup)'''


@bot.message_handler(commands=['start'])
def start(message):
    # ПЕРВЫЙ РАЗ -полное приветствие
    send_main_menu(message.chat.id, first_time=True)

# ===================================ОБРАБОТКА КНОПОК====================================


@bot.callback_query_handler(func=lambda callback: True)
def btn(callback):

    bot.answer_callback_query(callback.id)

    if callback.data == 'start':

        bot.edit_message_text(
            "🏋️ Напиши, какую группу упражнений делаешь:\n\n"
            "Примеры: 'Грудь', 'Спина + бицепс', 'Кардио 30 мин', 'Жим лежа'",
            callback.message.chat.id, callback.message.message_id)

        bot.register_next_step_handler(callback.message, save_start)

    if callback.data == 'end':
        user_id = callback.from_user.id
        name = callback.from_user.username or callback.from_user.first_name
        current_time = datetime.now().strftime("%d-%m-%Y, %H:%M")


        cursor.execute("""
        SELECT id, training, start_time 
        FROM workout
        WHERE user_id = ? AND end_time IS NULL
        ORDER BY id DESC
        LIMIT 1
        """,(user_id,))

        last_workout = cursor.fetchone()

        if last_workout:
            markup = types.InlineKeyboardMarkup()
            btn_menu = types.InlineKeyboardButton('Главное меню', callback_data='menu')
            markup.row(btn_menu)




            workout_id, training_name, start_time_str = last_workout         # распаковка кортежа из cursor.fetchone()


            start_time_obj = datetime.strptime(start_time_str, "%d-%m-%Y, %H:%M")
            end_time = datetime.now() #конец времени тренировки это то какое СЕЙЧАС время, то есть  datetime.now()
            minutes = (end_time - start_time_obj ).seconds // 60

            cursor.execute("""
                            UPDATE workout 
                            SET end_time = ?, minutes = ? 
                            WHERE id = ?
                        """, (current_time, minutes, workout_id))
            dp.commit()

            # Отправляем результат
            bot.send_message(
                callback.message.chat.id,
                f"✅ **Тренировка завершена, {name}!**\n\n"
                f"💪 {training_name}\n\n"
                f"🕐 Начало: {start_time_str}\n"
                f"🕐 Конец: {current_time}\n\n"
                f"⏱️ Продолжительность: {minutes} минут",reply_markup=markup)

        else:
            bot.send_message(
                callback.message.chat.id,
                f"❌ {name}, у вас нет активных тренировок!\n"
                "Нажми 'Начать' чтобы начать новую."
            )

    if callback.data == 'history':
        user_id = callback.from_user.id
        name = callback.from_user.username or callback.from_user.first_name

        cursor.execute("""SELECT start_time, training, minutes FROM workout WHERE user_id = ? ORDER BY id DESC 
        """, (user_id,))

        #history_info = cursor.fetchone()

        history_info = cursor.fetchall()

        if history_info:

            message = "📋 ТВОЯ ИСТОРИЯ ТРЕНИРОВОК:\n\n"

            for chislo, row in enumerate(history_info, 1): # enumerate добавляет номера, row распаковает кортеж
                start_time, training, minutes = row

                if minutes is None:

                    time_ON_or_OFF = "НЕ ЗАВЕРШЕНА"

                else:     time_ON_or_OFF = f"{int(minutes)} Минут"


                message += f"{chislo}. {start_time} - {training}\n\n"
                message += f"Продолжительность: {time_ON_or_OFF} минут\n"

            info = len(history_info)
            completed = len([workout for workout in history_info if workout[2] is not None])  # Считает сколько тренировок завершено (minutes не None)


            message += f"---\n"
            message += f"📊 Всего тренировок: {info}\n"
            message += f"✅ Завершено: {completed}\n"


            bot.send_message(callback.message.chat.id, message)


        else: bot.send_message(callback.message.chat.id, f"📭 {name}, у тебя ещё нет тренировок!")

    if callback.data == 'menu':

        send_main_menu(callback.message.chat.id, callback.message.message_id)


# ===================================ФУНКЦИИ====================================

def save_start(message):

    markup = types.InlineKeyboardMarkup()
    btn2_end = types.InlineKeyboardButton('Закончить', callback_data='end')

    markup.row(btn2_end)

    user_id = message.from_user.id #Получаем ID пользователя в Telegram
    name = message.from_user.username or message.from_user.first_name # username пользователя, если его нет берем имя

    training = message.text.strip()

    if training:

        start_time = datetime.now().strftime("%d-%m-%Y, %H:%M")  # Пример: 17 января 2024, 21:45:30

        cursor.execute("""INSERT INTO workout (user_id, name, training, start_time) VALUES (?, ?, ?, ?)""",
                       (user_id,name, training, start_time))
        dp.commit()

        bot.send_message(message.chat.id,f"✅ Тренировка начата!\n\n"
            f"💪 {training}\n"
            f"🕐 {start_time}\n\n"
            f"Не забудь нажать 'Закончить' когда закончишь!", reply_markup=markup)


def send_main_menu(chat_id, message_id=None, first_time=False):
    """Отправляет главное меню с кнопками"""
    markup = types.InlineKeyboardMarkup()
    btn1_start = types.InlineKeyboardButton('Начать', callback_data='start')
    btn2_end = types.InlineKeyboardButton('Закончить', callback_data='end')
    btn3_stats = types.InlineKeyboardButton('История', callback_data='history')

    markup.row(btn1_start, btn2_end)
    markup.row(btn3_stats)

    if first_time:
        # ПЕРВЫЙ РАЗ - полное приветствие
        message_text = (
            "🏋️ Simple Workout Tracker\n\n"
            "Привет! Я твой личный помощник для отслеживания тренировок. "
            "Я помогу тебе фиксировать прогресс и следить за временем в зале.\n\n"
            "Выберите действие на панели ниже:"
        )
    else:
        # НЕ первый раз - короткая версия
        message_text = ("🏋️ <b>Simple Workout Tracker МЕНЮ</b>\n\n"
                        '"Начать" — Запускает новую тренировку. '
                        'Бот спросит, какое упражнение или группу мышц ты делаешь, '
                        'запишет время начала и сохранит\n\n'
                        '"Закончить" — Завершает текущую активную тренировку. '
                        'Бот найдёт последнюю незавершённую тренировку, '
                        'запишет время окончания, посчитает продолжительность и сохранит результат.\n\n'
                        '"История" — Показывает список последних тренировок: когда, что делал и сколько времени заняло.\n\n'
                        'Выберите действия:',)
    if message_id:
        bot.edit_message_text(
            message_text,
            chat_id, message_id,
            reply_markup=markup,
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            chat_id,
            message_text,
            reply_markup=markup,
            parse_mode='HTML'
        )



bot.polling()




'''    

SELECT id, training, start_time — выбираем эти три столбца из найденных записей

FROM workout — из таблицы workout

WHERE user_id = ? — где user_id равен нашему (подставляем значение)

AND end_time IS NULL — И где end_time пустое (значит тренировка не завершена)

ORDER BY id DESC — сортируем по id в обратном порядке (от новых к старым)

LIMIT 1 — берём только одну (самую новую) запись

'''


'''

    UPDATE workout — обновляем таблицу workout

    SET end_time = ?, minutes = ? — устанавливаем значения для двух столбцов:

    end_time = текущее время завершения

    minutes = рассчитанная продолжительность

    WHERE id = ? — ТОЛЬКО для строки с конкретным id

Пример: Для записи с id=2:

Устанавливаем end_time = "17-01-2024, 16:15"

Устанавливаем minutes = 45

'''