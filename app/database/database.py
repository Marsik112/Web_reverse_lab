import sqlite3

def get_connection():
    conn = sqlite3.connect('bd_for_lab.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    connection = get_connection()
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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL UNIQUE,
        raw_data_file TEXT,
        raw_data_strings TEXT,
        FOREIGN KEY (file_id) REFERENCES files(id)
                   ON DELETE CASCADE
                   ON UPDATE CASCADE
    ) 
    ''')

    connection.commit()
    connection.close()
    return 0


def add_file(filename, size, status):
    connection = get_connection()
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
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""SELECT * FROM files""")
    file_list = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return file_list

def file_info(file_id):
    connection = get_connection()
    cursor = connection.cursor()

    sql = """SELECT * FROM files
            WHERE id = ?"""
    data_sql = (file_id,)
    cursor.execute(sql, data_sql)
    file = cursor.fetchone()
    
    connection.close()
    return dict(file) if file != None else None

def add_analisys(file_id, raw_data, raw_data_strings):
    connection = get_connection()
    cursor = connection.cursor()

    search_result = get_analysis(file_id)
    if search_result == None:
        sql ="""INSERT INTO analysis (file_id, raw_data_file, raw_data_strings)
            VALUES(?, ?, ?)
        """
        data_sql = (file_id, raw_data, raw_data_strings)

        cursor.execute(sql, data_sql)
    else:
        sql ="""UPDATE analysis SET raw_data_file = ?, raw_data_strings = ? WHERE file_id = ?"""
        data_sql = (raw_data, raw_data_strings, file_id)

        cursor.execute(sql, data_sql)
    connection.commit()
    connection.close()
    return 0

def get_analysis(file_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM analysis WHERE file_id = ?""", (file_id,))
    search_result = cursor.fetchone()
    connection.close()
    return search_result