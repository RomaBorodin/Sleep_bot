import sqlite3 as sq


def tables_creation():
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        queries = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sleep_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_time VARCHAR(50),
            duration VARCHAR(50),
            sleep_quality INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sleep_record_id INTEGER,
            note TEXT,
            FOREIGN KEY (sleep_record_id) REFERENCES sleep_records(id)
        )
        '''
        cur.executescript(queries)
        cur.close()


def get_last_record(user_id):
    with sq.connect('sleep.db') as con:
        con.row_factory = sq.Row
        cur = con.cursor()

        query = '''
        SELECT * FROM sleep_records
        WHERE user_id = ?
        ORDER BY start_time DESC
        '''
        record = cur.execute(query, (user_id,)).fetchone()
        cur.close()

        return record


def find_user(user_id):
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        query = '''
        SELECT id FROM users
        WHERE id = ?
        '''
        user = cur.execute(query, (user_id,)).fetchone()
        cur.close()

        return user


def add_user(user_id, user_name):
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        query = '''
        INSERT INTO users (id, name) VALUES (?, ?)
        '''
        cur.execute(query, (user_id, user_name))
        con.commit()
        cur.close()


def add_start_time(user_id, start_time):
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        query = '''
        INSERT INTO sleep_records (user_id, start_time) VALUES (?, ?)
        '''
        cur.execute(query, (user_id, start_time))
        con.commit()
        cur.close()


def add_duration(duration, record_id):
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        query = '''
        UPDATE sleep_records
        SET duration = ?
        WHERE id = ?
        '''
        cur.execute(query, (duration, record_id))
        con.commit()
        cur.close()


def add_quality(quality, record_id):
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        query = '''
        UPDATE sleep_records
        SET sleep_quality = ?
        WHERE id = ?
        '''
        cur.execute(query, (quality, record_id))
        con.commit()
        cur.close()


def add_note(record_id, note):
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        query = '''
        INSERT INTO notes (sleep_record_id, note) VALUES (?, ?)
        '''
        cur.execute(query, (record_id, note))
        con.commit()
        cur.close()


def check_notes(record_id):
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        query = '''
        SELECT note FROM notes
        WHERE sleep_record_id = ?
        '''
        check = cur.execute(query, (record_id,)).fetchone()
        cur.close()

        return check


def get_notes(record_id):
    with sq.connect('sleep.db') as con:
        cur = con.cursor()

        query = '''
        SELECT note FROM notes
        WHERE sleep_record_id = ?
        '''
        notes = cur.execute(query, (record_id,)).fetchall()
        cur.close()

        return notes
