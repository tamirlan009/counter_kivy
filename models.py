import sqlite3

db = sqlite3.connect('DataBase.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS numbers (
            number TEXT
) """)

db.commit()
