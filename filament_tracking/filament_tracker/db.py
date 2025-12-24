import sqlite3
from flask import g, current_app


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config["DB_PATH"])
        db.row_factory = sqlite3.Row
    return db


def close_db(exception=None):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db(app):
    # register teardown
    app.teardown_appcontext(close_db)

    # init schema
    with app.app_context():
        db = get_db()
        c = db.cursor()

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS spools (
                id INTEGER PRIMARY KEY,
                name TEXT,
                brand TEXT,
                color TEXT,
                start_grams REAL,
                diameter_mm REAL,
                material TEXT,
                density_g_cm3 REAL,
                created_at TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS usages (
                id INTEGER PRIMARY KEY,
                spool_id INTEGER,
                used_grams REAL,
                used_length_m REAL,
                note TEXT,
                created_at TEXT,
                FOREIGN KEY(spool_id) REFERENCES spools(id)
            )
            """
        )

        db.commit()
