import sqlite3

db = sqlite3.connect('ZTTao.db')# Создал БД/Подключиться к БД

c = db.cursor()

#c.execute("""CREATE TABLE articles (
#title text,
#full_text text,
#views_integer,
#avtor text
# )""")  #execute позволяет нам написать SQL команду

#-------------------------------------------------------------------------------

# Добавление данных

#.cexecute("INSERT INTO articles VALUES('ZTTao is cool!', 'ZTTao is realy cool!', 999, 'Fr1nd')")

#-------------------------------------------------------------------------------

#Выборка данных

c.execute("SELECT * FROM articles")
hui = (c.fetchall())
#print(c.fetchmany(1)) # Вывод вместе с кортежем
#print(c.fetchone()[1])    # Вывод вместе с списком

for hi in hui:
    print(hui)


'''-- Только дата (без времени)
created_at TEXT DEFAULT (date('now'))

-- Только время
created_at TEXT DEFAULT (time('now'))

-- Только дата в формате ДД.ММ.ГГГГ
created_at TEXT DEFAULT (strftime('%d.%m.%Y', 'now'))'''


db.commit()

db.close()# Закрыл БД