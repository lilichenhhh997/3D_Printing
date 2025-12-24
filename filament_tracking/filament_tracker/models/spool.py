from ..db import get_db

def list_spools():
    return get_db().execute(
        "SELECT * FROM spools ORDER BY created_at DESC"
    ).fetchall()

def get_spool(spool_id):
    return get_db().execute(
        "SELECT * FROM spools WHERE id = ?",
        (spool_id,)
    ).fetchone()

def create_spool(data):
    db = get_db()
    db.execute(
        """
        INSERT INTO spools (name,brand,color,start_grams,material,created_at)
        VALUES (?,?,?,?,?,?)
        """,
        (
            data["name"],
            data["brand"],
            data["color"],
            data["start_grams"],
            data["material"],
            data["created_at"],
        ),
    )
    db.commit()
