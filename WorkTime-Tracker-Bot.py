import telebot
import sqlite3
from config import TOKEN
from telebot import types
from datetime import datetime
from config import ADMIN_ID

bot = telebot.TeleBot(TOKEN)




dp = sqlite3.connect('DV_LINK.db', check_same_thread=False)

cursor = dp.cursor()


#cursor.execute("DROP TABLE IF EXISTS work")

cursor.execute("""CREATE TABLE IF NOT EXISTS work (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
name TEXT,
start_time TEXT,
end_time TEXT,
hours REAL,
many REAL,
workout_date TEXT DEFAULT (DATETIME('now', 'localtime'))
)
""")

dp.commit()





@bot.message_handler(commands=["start"])
def start(message):

    name = message.from_user.username or message.from_user.first_name

    markup = types.InlineKeyboardMarkup()
    btn_1_start = types.InlineKeyboardButton("Начать работу", callback_data='start')
    btn_2_end = types.InlineKeyboardButton("Закончить работу", callback_data='end')
    btn_3_info = types.InlineKeyboardButton("Статистика", callback_data='stats')

    markup.row(btn_1_start,btn_2_end)
    markup.row(btn_3_info)

    bot.send_message(message.chat.id, f"Зраствуйте, <b>{name}</b>.👋 \n\n"
                                      f"Это бот для счета отработанных часов и зарплаты.\n\n"
                                      f"Выберите действие:", reply_markup=markup, parse_mode='HTML')



@bot.message_handler(commands=["cler_full_base"])
def cler(message):

    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ У вас нет прав для этой команды!")
        return

    markup = types.InlineKeyboardMarkup()

    btn_yes = types.InlineKeyboardButton('✅ Да, очистить', callback_data='clear_yes')
    btn_no = types.InlineKeyboardButton('❌ Нет, отмена', callback_data='clear_no')

    markup.row(btn_yes, btn_no)

    bot.reply_to(message,"⚠️ <b>Внимание! Вы собираетесь удалить ВСЕ данные из базы.</b>\n\n"
                 "Это действие нельзя отменить!\n\n"
                 "Вы уверены?",
                 reply_markup=markup, parse_mode='HTML')








@bot.callback_query_handler(func=lambda callback: True)
def btn(callback):

    bot.answer_callback_query(callback.id)

    if callback.data == "start":

        user_id = callback.from_user.id  # Получаем ID пользователя в Telegram
        name = callback.from_user.username or callback.from_user.first_name  # username пользователя, если его нет берем имя

        start_time = datetime.now().strftime("%d-%m-%Y, %H:%M")


        cursor.execute("""INSERT INTO work (user_id, name, start_time) VALUES (?,?,?) """,
        (user_id, name, start_time))

        dp.commit()



        markup = types.InlineKeyboardMarkup()
        btn_2_end = types.InlineKeyboardButton("Закончить работу", callback_data='end')
        markup.row(btn_2_end)

        bot.edit_message_text(f"✅ <b>Работа начата!</b>\n\n"
                              f"🕐 {start_time}\n\n"
                              f"Не забудь нажать 'Закончить' когда закончите!",
                              chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id,
                              parse_mode="HTML",
                              reply_markup=markup)
        # БЛЯТЬ, СЛУШАЙ СЮДА:
        # callback.message.chat.id - это ID чата (беседы), где была нажата кнопка
        # Без этого бот не поймет, в каком чате искать сообщение для редактирования



    if callback.data == "end":

        user_id = callback.from_user.id
        name = callback.from_user.username or callback.from_user.first_name
        end_time_str = datetime.now().strftime("%Y-%m-%d, %H:%M")
        end_time = datetime.now()  # конец времени тренировки это то какое СЕЙЧАС время, то есть  datetime.now()


        cursor.execute("""
                        SELECT id, start_time 
                        FROM work
                        WHERE user_id = ? AND end_time IS NULL
                        ORDER BY id DESC
                        LIMIT 1
                        """, (user_id,))

        last_work = cursor.fetchone()


        if last_work:
            markup = types.InlineKeyboardMarkup()
            btn_menu = types.InlineKeyboardButton('Главное меню', callback_data='menu')
            markup.row(btn_menu)

            work_id,  start_time_str = last_work

            start_time_obj = datetime.strptime(start_time_str, "%d-%m-%Y, %H:%M")


            time_difference = end_time - start_time_obj

            info_time = time_difference.total_seconds()

            hours = round(info_time / 3600, 2)

            #minutes = (end_time - start_time_obj).seconds // 60
            many = round(hours * 400, 2)

            cursor.execute("""UPDATE work SET end_time = ?, hours = ?, many = ? WHERE id = ?""",
               (end_time_str, hours, many, work_id))


            dp.commit()

            bot.send_message(callback.message.chat.id,
                             f"✅ <b>Работа завершена</b> в {end_time_str}!\n\n"
                             f"👤 Пользователь: <b>{name}</b>\n"
                             f"⏱️ Отработано: {hours} часов\n"
                             f"💰 Заработано: {many} руб.", reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(
                callback.message.chat.id,
                f"❌ <b>{name}</b>, у вас <b>нет активных смен!</b>\n"
                "Нажми 'Начать' чтобы начать новую.", parse_mode="HTML"
            )


    if callback.data == "menu":

        markup = types.InlineKeyboardMarkup()
        btn1_start = types.InlineKeyboardButton('Начать', callback_data='start')
        btn2_end = types.InlineKeyboardButton('Закончить', callback_data='end')
        btn3_stats = types.InlineKeyboardButton('Статистика', callback_data='stats')

        markup.row(btn1_start, btn2_end)
        markup.row(btn3_stats)

        bot.send_message(callback.message.chat.id, "👷 <b>ГББ: Центр управления работой</b> 👷\n\n"
                                                   '"<b>Начать</b>" — Начинает новую рабочую смену. '
                                                   'Бот сообщит что смена началась и запишет ее начало, посчитает сколько заработано.\n\n'
                                                   '"<b>Закончить</b>" — Завершает текущую активную смену. '
                                                   'Бот найдёт последнюю незавершённую смену, '
                                                   'запишет время окончания, посчитает ее продолжительность вместе с зарплатой, '
                                                   'и сохранит результат.\n\n'
                                                   '"<b>Статистика</b>" — Показывает вашу персональную статистику '
                                                   'или общую статистику всех пользователей.'
                                                   'Можно посмотреть сколько часов отработано и сколько заработано денег.\n\n'
                                                   'Выберите действия:', reply_markup=markup, parse_mode="HTML")

    if callback.data == "stats":
        markup = types.InlineKeyboardMarkup()
        btn1_me_stats = types.InlineKeyboardButton('Моя статистика', callback_data='me_stats')
        btn2_global_stats = types.InlineKeyboardButton('Общая статистика', callback_data='global_stats')

        markup.row(btn1_me_stats, btn2_global_stats)

        bot.edit_message_text("Выбери подходящую статистику:",
                              chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id,
                              reply_markup=markup)

    elif callback.data == "me_stats":
        user_id = callback.from_user.id
        name = callback.from_user.username or callback.from_user.first_name

        # ВСЕ записи пользователя
        cursor.execute("""SELECT * FROM work WHERE user_id = ?""", (user_id,))
        all_records = cursor.fetchall()

        summa_sessions = 0
        summa_hors = 0
        summa_money = 0

        for record in all_records:
            # record[5] = hours, record[6] = many, смотреть задание #1 по БД
            if record[5] is not None:  # если есть часы (значит сессия завершена) смотреть БД и тг Simple Workout Tracker
                summa_sessions += 1
                summa_hors += record[5] or 0
                summa_money += record[6] or 0

        if summa_sessions > 0:
            message_text = (
                f'Статистика пользователя: <b>{name}</b>\n\n'
                f'📅 Всего: {summa_hors} часов\n'
                f'💰 Заработано: {summa_money} руб\n\n'
                f'📋 Всего рабочих сессий: {summa_sessions}\n'
                f'💵 Ставка: 400 руб./час'
            )
        else:
            message_text = (
                f'📊 Статистика пользователя: {name}\n\n'
                f'📅 Всего: 0 часов\n'
                f'💰 Заработано: 0 руб\n\n'
                f'📋 Всего рабочих сессий: 0\n'
                f'💵 Ставка: 400 руб./час'
            )

        bot.edit_message_text(
            message_text,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            parse_mode="HTML"
        )

    elif callback.data == "global_stats":

        cursor.execute("""SELECT DISTINCT user_id, name FROM work""")
        all_users = cursor.fetchall()

        if not all_users:
            bot.edit_message_text("📊 <b>Общая статистика:</b>\n\nНет данных о пользователях",
                                  chat_id=callback.message.chat.id,
                                  message_id=callback.message.message_id)
            return

        message_info = "📊 <b>Общая статистика:</b>\n\n"

        # Для каждого пользователя считаем статистику
        for user_id, user_name in all_users:
            cursor.execute("""SELECT * FROM work WHERE user_id = ?""", (user_id,))
            user_records = cursor.fetchall()

            summa_sessions = 0
            summa_hors = 0
            summa_money = 0

            for record in user_records:
                if record[5] is not None:
                    summa_sessions +=1
                    summa_hors += record[5] or 0
                    summa_money += record[6] or 0

            message_info += (
                f"👤 <b>{user_name}</b>:\n"
                f"   📅 Всего: {summa_hors} ч.\n"
                f"   💰 Зарплата: {summa_money} руб.\n"
                f"   📋 Всего рабочих сессий: {summa_sessions}\n"
                f"   💵 Ставка: 400 руб./час\n\n"
            )

        bot.edit_message_text(
            message_info,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            parse_mode="HTML"
        )

    if callback.data == "clear_yes":
        # очистка базы
        cursor.execute("DELETE FROM work")
        dp.commit()
        # Пересоздаём таблицу
        cursor.execute("DROP TABLE IF EXISTS work")
        cursor.execute("""CREATE TABLE IF NOT EXISTS work (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        hours REAL,
                        many REAL,
                        workout_date TEXT DEFAULT (DATETIME('now', 'localtime'))
                    )""")
        dp.commit()

        bot.edit_message_text("✅ <b>База данных полностью очищена!</b> Все данные удалены.", chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id,
                              parse_mode="HTML")
    if callback.data == 'clear_no':
        bot.edit_message_text("❌ <b>Очистка базы данных отменена.</b>",
                              chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id,
                              parse_mode="HTML")
        return





bot.polling()

'''name = callback.from_user.username or callback.from_user.first_name

        cursor.execute("""SELECT * FROM work """)

        global_info_stats = cursor.fetchall()

        summa_sessions = 0
        summa_hors = 0
        summa_money = 0

        for record in global_info_stats:
            # record[5] = hours, record[6] = many, смотреть задание #1 по БД
            if record[5] is not None:  # если есть часы (значит сессия завершена) смотреть БД и тг Simple Workout Tracker
                summa_sessions += 1
                summa_hors += record[5] or 0
                summa_money += record[6] or 0

        if summa_sessions > 0:
            message_text = (
                f'Статистика пользователя: {name}\n\n'
                f'📅 Всего: {summa_hors} часов\n'
                f'💰 Заработано: {summa_money} руб\n\n'
                f'📋 Всего рабочих сессий: {summa_sessions}\n'
                f'💵 Ставка: 400 руб./час'
            )
        else:
            message_text = (
                f'📊 Статистика пользователя: {name}\n\n'
                f'📅 Всего: 0 часов\n'
                f'💰 Заработано: 0 руб\n\n'
                f'📋 Всего рабочих сессий: 0\n'
                f'💵 Ставка: 400 руб./час'
            )

        bot.edit_message_text(
            message_text,
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )

'''

''' cursor.execute("""SELECT id, hours, many FROM work WHERE user_id = ? """,(user_id,))


            info_me_stats =  cursor.fetchone()

            if info_me_stats:

                message_text = f"Статистика пользователя: {name}\n\n"

                for i, row in enumerate(info_me_stats, 1):

                    id, hours, many = row

                    if  hours is None:
                        duration_text  = "не завершена"
                    else:
                        duration_text = f"{int(hours)} минут"

                        message_text += f"{i}. {id} - {many}\n"
                        message_text += f"   ⏱️ {duration_text}\n\n"

                total = len(info_me_stats)
                completed = len([work for work in info_me_stats if work[2] is not None])

                message_text += f"---\n"
                message_text += f"📊 Всего тренировок: {total}\n"
                message_text += f"✅ Завершено: {completed}\n"

                bot.send_message(callback.message.chat.id, message_text)

            else:
                bot.send_message(
                    callback.message.chat.id,
                    f"📭 {name}, у тебя ещё нет тренировок!"
                )

'''



'''id, hours, many = info_me_stats

                bot.edit_message_text(f'Статистика пользователя: {name}\n\n'
                                      f'📅 Всего: {hours} часов\n'
                                      f'💰 Заработано : {many} руб\n\n'
                                      f'📋 Всего рабочих сессий: {}')'''


'''📊 Статистика пользователя: ZenithTech TAO

📅 Сегодня: 0.00 часов
💰 Заработано сегодня: 3.19 руб.

📅 За неделю: 0.00 часов
💰 Заработано за неделю: 3.19 руб.

📋 Всего рабочих сессий: 1
💵 Ставка: 1000 руб./час

—————————————————————————


📊 Общая статистика за сегодня:

👤 ZenithTech TAO:
   ⏱️ Часы: 0.00
   💰 Зарплата: 3.19 руб.

📈 Итого за день:
   ⏱️ Всего часов: 0.00
   💰 Общая зарплата: 3.19 руб.'''



'''def save_start():
    markup = types.InlineKeyboardMarkup()
    btn_2_end = types.InlineKeyboardButton("Закончить работу", callback_data='end')
    markup.row(btn_2_end)


    start_time = datetime.now().strftime("%d-%m-%Y, %H:%M")
    bot.edit_message_text(f"✅ Тренировка начата!\n\n"
                          f"🕐 {start_time}\n\n"
                          f"Не забудь нажать 'Закончить' когда закончишь!", reply_markup=markup)'''


