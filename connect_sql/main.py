import sqlite3 as sqlite

connection = sqlite.connect('data.db')
cursor = connection.cursor()

cursor.execute("SELECT band, date FROM events WHERE date='2088.10.15'")
print(cursor.fetchall())

# Insert new rows
# new_rows = [('Lions', 'Lion City', '2088.10.15'),
#             ('Monkey', 'Monkey City', '2088.10.15')]
#
# cursor.executemany("INSERT INTO events VALUES(?,?,?)", new_rows)
# connection.commit()