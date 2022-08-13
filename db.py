import sqlite3


def get_connection():
    return sqlite3.connect('data.sqlite3')


def init_db():
    conn = get_connection()
    data = conn.cursor()
    info = conn.cursor()
    data.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL
        )
    ''')

    info.execute('''
        CREATE TABLE IF NOT EXISTS info (
            id          INTEGER PRIMARY KEY,
            info        TEXT NOT NULL,
            data_id     INTEGER NOT NULL,
            FOREIGN KEY (data_id) REFERENCES data (id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')
    conn.commit()


def add_data(name: str):
    conn = get_connection()
    c = conn.cursor()

    c.execute('SELECT * FROM data WHERE name =?', (name,))
    result = c.fetchone()
    if result is not None:
        conn.close()
        return False  # not created
    else:
        c.execute('INSERT INTO data (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        return True


def add_info(name: str, info: str):
    conn = get_connection()
    c = conn.cursor()
    obj = c.execute('SELECT id FROM data WHERE name =?', (name,))
    (data_id,) = obj.fetchone()
    c.execute('INSERT INTO info (info, data_id) VALUES (?, ?)', (info, data_id,))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
