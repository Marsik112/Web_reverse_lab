import sqlite3
import json

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
        analysis_time TEXT NOT NULL,
        file_result TEXT,
        strings_output TEXT,
        sha256 TEXT,
        FOREIGN KEY (file_id) REFERENCES files(id)
                   ON DELETE CASCADE
                   ON UPDATE CASCADE
    ) 
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ghidra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL UNIQUE,
        analysis_time TEXT NOT NULL,
        func_json TEXT,
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

def add_analisys(file_id, file_result, strings_output, sha256):
    connection = get_connection()
    cursor = connection.cursor()

    search_result = get_analysis(file_id)
    if search_result == None:
        sql ="""INSERT INTO analysis (file_id, analysis_time,  file_result, strings_output, sha256)
            VALUES(?, datetime('now'),?, ?, ?)
        """
        data_sql = (file_id, file_result, strings_output, sha256)

        cursor.execute(sql, data_sql)
    else:
        sql ="""UPDATE analysis SET file_result = ?, strings_output = ?, sha256 = ? WHERE file_id = ?"""
        data_sql = (file_result, strings_output, file_id, sha256)

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
    return dict(search_result) if search_result != None else None

def delete_file(file_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""DELETE FROM files WHERE id = ?""", (file_id,))
    connection.commit()
    connection.close()

def get_ghidra(file_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM ghidra WHERE file_id = ?""", (file_id,))
    search_result = cursor.fetchone()
    connection.close()
    return dict(search_result) if search_result != None else None

def add_ghidra(file_id, ghidra_func):
    connection = get_connection()
    cursor = connection.cursor()
    search_result = get_ghidra(file_id)
    ghidra_func_json = json.dumps(ghidra_func)
    if search_result == None:
        sql ="""INSERT INTO ghidra (file_id, analysis_time, func_json)
            VALUES(?, datetime('now'),?)
        """
        data_sql = (file_id, ghidra_func_json,)

        cursor.execute(sql, data_sql)
    else:
        sql ="""UPDATE ghidra SET analysis_time = datetime('now'), func_json = ? WHERE file_id = ?"""
        data_sql = (ghidra_func_json, file_id)
        cursor.execute(sql, data_sql)
    
    connection.commit()
    connection.close()
    return 0