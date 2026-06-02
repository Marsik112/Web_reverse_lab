import sqlite3
def init_db():
    connection = sqlite3.connect('bd_for_lab.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        size INTEGER NOT NULL,
        upload_time TEXT NOT NULL,
        status TEXT NOT NULL
    ) 
    ''')

    connection.commit()
    connection.close()
    return 0


def add_file(filename, size, status):
    connection = sqlite3.connect('bd_for_lab.db')
    cursor = connection.cursor()
    
    sql = """
    INSERT INTO files (filename, size, upload_time, status)
    VALUES(?, ?, datetime('now'), ?)
    """
    file_data = (filename, size, status)
    
    cursor.execute(sql, file_data)
    
    id_file = cursor.lastrowid
    
    connection.commit()
    connection.close()
    return id_file

def list_files():
    connection = sqlite3.connect('bd_for_lab.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""SELECT * FROM files""")
    file_list = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return file_list

def file_info(file_id):
    connection = sqlite3.connect('bd_for_lab.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    sql = """SELECT * FROM files
            WHERE id = ?"""
    data_sql = (file_id,)
    cursor.execute(sql, data_sql)
    file = cursor.fetchone()
    
    connection.close()
    return file