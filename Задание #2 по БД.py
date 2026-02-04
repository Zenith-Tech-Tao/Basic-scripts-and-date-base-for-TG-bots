import sqlite3

db = sqlite3.connect('Задание #2 по БД.db')

c = db.cursor()

#c.execute("DROP TABLE IF EXISTS reviews") #-- удаление данных

#1.1 - Создание таблиц в SQLite

c.execute("""CREATE TABLE IF NOT EXISTS movies

(
id	INTEGER PRIMARY KEY AUTOINCREMENT,
title	TEXT,
year	INTEGER,
genre	TEXT,
director	TEXT,
avg_rating	REAL
)

""")


c.execute("""CREATE TABLE IF NOT EXISTS reviews
(
id INTEGER PRIMARY KEY AUTOINCREMENT, 
movie_id INTEGER,
reviewer TEXT,
rating INTEGER,
comment TEXT,
review_date TEXT
)
""")



#1.2 - Добавление тестовых данных

c.execute("INSERT OR IGNORE INTO movies VALUES ('1', 'Тень Сицилии', '2021', 'Криминальная драма, триллер', 'Паоло Соррентино','8.2/10') ")
c.execute("INSERT OR IGNORE INTO movies VALUES ('2', 'Последний сигнал Оберона', '2018', 'Научная фантастика, приключения', ' Дени Вильнёв', '7.9/10') ")
c.execute("INSERT OR IGNORE INTO movies VALUES ('3', 'Красные пески', '2015', 'Историческая драма, вестерн', 'Джейн Кэмпион', '8.5/10') ")
c.execute("INSERT OR IGNORE INTO movies VALUES ('4', 'Голос в статике', '2023', 'Психологический хоррор', ' Ари Астер', '7.1/10') ")
c.execute("INSERT OR IGNORE INTO movies VALUES ('5', 'Вне хронометража', '2019', 'Комедия, абсурд', ' Квентин Дюпье', '6.8/10') ")


#1.3 -  Функция показа всех фильмов
def print_info():
    c.execute("SELECT * FROM movies")

    info = c.fetchall()
    for inf in info:

        print(f"🎬 {inf[0]}. {inf[1]} ({inf[2]}) \n"
              f"📍 Жанр: {inf[3]} \n"
              f"👨‍🎨 Режиссер: {inf[4]} \n"
              f"⭐ Рейтинг: {inf[5]}\n\n")




def proverka_stop(delete):
    # Запрашиваем ввод с переданным приглашением
    request = input(delete)

    # Если пользователь ввел '1', возвращаем None (отмена)
    if request.lower() == '1':
        return None

    # Иначе возвращаем введенное значение
    return request


#print_info()



#1.4 - Функция добавления фильма
def new_movies():
    print("\n=== ДОБАВЛЕНИЕ ФИЛЬМА ===")
    print("Вы выбрали: Добавить новый фильм")
    print("\nЕсли передумаете, то введите '1'")

    title = proverka_stop("Название фильма: ")
    if title is None:
        print("Конец работы")
        return
    year = proverka_stop("Год выхода:")
    if year is None:
        print("Конец работы")
        return
    genre = proverka_stop("Жанр:")
    if genre is None:
        print("Конец работы")
        return

    director = proverka_stop("Режиссер:")
    if director is None:
        print("Конец работы")
        return

    avg_rating = proverka_stop("Введите рейтинг. Пример: (3.2/10)")
    if avg_rating is None:
        print("Конец работы")
        return


    c.execute("INSERT OR IGNORE INTO movies (title ,year, genre,director, avg_rating ) VALUES (?, ?, ?, ?, ?)",
              (title, year,  genre, director, avg_rating))

    db.commit()
    print("Фильм добавлен!")


#new_movies()



#2.1 -  Функция показа всех фильмов для 2.2
def print_info_movies_in_reviews():
    c.execute("SELECT * FROM movies")

    info_movies_in_reviews = c.fetchall()
    for inf_rev in info_movies_in_reviews:
        print(f"{inf_rev[0]}. {inf_rev[1]} ({inf_rev[2]}) {inf_rev[5]}")






#2.2 Функция добавления отзыва
def new_reviews():
    print("Вы выбрали: Оставить отзыв")

    print("\n\nСписок фильмов:")
    print_info_movies_in_reviews()
    print("\nЕсли передумаете, то введите '1' ")
    
    movie_id = proverka_stop("\nВыберите ID фильма:")
    if movie_id is None:
        print("Конец работы")
    
    
    reviewer = proverka_stop("Ваше имя:")
    if reviewer is None:
        print("Конец работы")
        return

    rating = input("Ваша оценка (1-10):")

    comment = proverka_stop("Ваш комментарий:")
    if comment is None:
        print("Конец работы")
        return


    c.execute("INSERT OR IGNORE INTO reviews (movie_id ,reviewer, rating, comment) VALUES (?, ?, ?, ?)",
              (movie_id, reviewer,  rating, comment))
    db.commit()
    print("✅ Ваш отзыв добавлен!")


#new_reviews()

#2.3.1 Функция для показа отзывов к фильму
'''def print_reviews():
    c.execute("SELECT * FROM reviews")

    print_reviews = c.fetchall()
    for print_rev in print_reviews:
        print(f"📝 ОТЗЫВ #{print_rev[0]}:\n"
              f"👤 Автор: {print_rev[2]}\n"
              f"⭐ Оценка: {print_rev[3]}\n" 
              f"💬 Комментарий: {print_rev[4]}\n\n")'''

#2.3.2  Функция для показа отзывов к фильму (ИИ)
def print_reviews():
    print("\n=== ВСЕ ОТЗЫВЫ ===")

    # JOIN - связываем отзывы с фильмами
    c.execute("""
        SELECT 
            reviews.id,
            reviews.reviewer,
            reviews.rating,
            reviews.comment,
            movies.title,
            movies.id as movie_id
        FROM reviews
        JOIN movies ON reviews.movie_id = movies.id
        ORDER BY reviews.id
    """)

    reviews = c.fetchall()

    for review in reviews:
        print(f"\n📝 Отзыв #{review[0]} ")
        print(f"   🎬 Фильм: {review[4]}")
        print(f"   👤 Автор: {review[1]}")
        print(f"   ⭐ Оценка: {review[2]}/10")
        print(f"   💬 Комментарий: {review[3]}")

    print(f"\nВсего отзывов: {len(reviews)}")



#2.4 Функция дляавтоматического обнавления рейтинга
def plus_rating(movie_id):

    c.execute("SELECT rating FROM reviews WHERE movie_id = ?",
              (movie_id,))
    ratings = c.fetchall()
    if ratings:  # если есть отзывы
        # Считаем среднее
        total = 0
        for r in ratings:
            total += r[0]  # r[0] это рейтинг

        avg = total / len(ratings)

        # Обновляем в таблице movies
        c.execute("UPDATE movies SET avg_rating = ? WHERE id = ?", (avg, movie_id))
        db.commit()


#print_reviews()

#print_info()


#3 МЕНЮ
def menu():
    while True:
        print("\n" + "=" * 50)
        print("=== МЕНЮ ===")
        print("=" * 50)
        print("1. 📋 Показать все фильмы")
        print("2. ➕ Добавить фильм")
        print("3. ✅ Добавить отзыв")
        print("4. 👀 Посмотреть отзывы")
        print("0. 🚪 Выйти")
        print("=" * 50)

        send_message = input("Выберите действие (о-4): ")

        if send_message == '1':
            print_info()
        elif send_message == '2':
            new_movies()
        elif send_message == '3':
            new_reviews()
        elif send_message == '4':
            print_reviews()
        elif send_message == '0':
            print("\n👋 До свидания!")
            break
        else:
            print("❌ Ошибка! Введите число от 0 до 4")



menu()

db.close()



