# filament_tracker/routes/export.py
import csv
import io
from flask import Blueprint, send_file

from ..db import get_db
from ..services.inventory import remaining_for_spool

bp = Blueprint("export", __name__)


@bp.route("/api/export/csv", methods=["GET"])
def export_csv():
    db = get_db()
    cur = db.execute("SELECT * FROM spools")
    spools = [dict(r) for r in cur.fetchall()]

    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(
        [
            "spool_id",
            "name",
            "brand",
            "color",
            "start_grams",
            "material",
            "created_at",
            "remaining_grams",
        ]
    )

    for s in spools:
        rem = remaining_for_spool(s["id"])
        w.writerow(
            [
                s.get("id"),
                s.get("name"),
                s.get("brand"),
                s.get("color"),
                s.get("start_grams"),
                s.get("material"),
                s.get("created_at"),
                rem if rem is not None else 0.0,
            ]
        )

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="filaments.csv",
    )
