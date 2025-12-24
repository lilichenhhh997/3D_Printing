# filament_tracker/services/inventory.py
from ..db import get_db


def remaining_for_spool(spool_id: int):
    """calculate remaining：start_grams - sum(used_grams)。"""
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT start_grams FROM spools WHERE id = ?", (spool_id,))
    row = cur.fetchone()
    if not row:
        return None

    start = row["start_grams"] or 0.0

    cur.execute(
        "SELECT IFNULL(SUM(used_grams),0) AS s FROM usages WHERE spool_id = ?",
        (spool_id,),
    )
    used = cur.fetchone()["s"] or 0.0

    return round(start - used, 2)
