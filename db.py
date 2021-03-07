import sqlite3


conn = sqlite3.connect("database.db")
cursor = conn.cursor()
sql = '''
CREATE TABLE Users (
id integer PRIMARY KEY,
state text


);
'''
cursor.execute(sql)
conn.commit()