import sqlite3

conn = sqlite3.connect("wydatki.db")
c = conn.cursor()


def usun():
    query = "DELETE FROM zakupy"
    c.execute(query)
    conn.commit()

usun()