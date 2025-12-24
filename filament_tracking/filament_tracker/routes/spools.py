# filament_tracker/routes/spools.py
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime

from ..db import get_db
from ..services.inventory import remaining_for_spool

bp = Blueprint("spools", __name__, url_prefix="/api/spools")


@bp.route("", methods=["GET", "POST"])
def api_spools():
    db = get_db()

    if request.method == "POST":
        data = request.json or {}
        name = data.get("name") or "untitled"
        brand = data.get("brand") or ""
        color = data.get("color") or ""
        material = data.get("material") or "" 

        try:
            start_grams = float(data.get("start_grams") or 0.0)
        except ValueError:
            return jsonify({"error": "invalid start_grams"}), 400

        db.execute(
            """
            INSERT INTO spools
            (name,brand,color,start_grams,diameter_mm,material,density_g_cm3,created_at)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                name,
                brand,
                color,
                start_grams,
                None,
                material,
                None,
                datetime.now(current_app.config["TZ"]).isoformat(),
            ),
        )
        db.commit()
        return jsonify({"ok": True}), 201

    # GET
    cur = db.execute("SELECT * FROM spools ORDER BY created_at DESC")
    spools = [dict(r) for r in cur.fetchall()]
    for s in spools:
        rem = remaining_for_spool(s["id"])
        s["remaining_grams"] = rem if rem is not None else 0.0
    return jsonify(spools)


@bp.route("/<int:spool_id>", methods=["GET", "PUT", "DELETE"])
def api_spool(spool_id):
    db = get_db()

    cur = db.execute("SELECT * FROM spools WHERE id = ?", (spool_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404

    if request.method == "GET":
        s = dict(row)
        s["remaining_grams"] = remaining_for_spool(spool_id) or 0.0
        return jsonify(s)

    if request.method == "PUT":
        data = request.json or {}
        name = data.get("name") or "untitled"
        brand = data.get("brand") or ""
        color = data.get("color") or ""
        material = data.get("material") or ""

        try:
            start_grams = float(data.get("start_grams") or 0.0)
        except ValueError:
            return jsonify({"error": "invalid start_grams"}), 400

        db.execute(
            """
            UPDATE spools
            SET name=?,brand=?,color=?,start_grams=?,material=?
            WHERE id=?
            """,
            (name, brand, color, start_grams, material, spool_id),
        )
        db.commit()
        return jsonify({"ok": True})

    # DELETE
    db.execute("DELETE FROM usages WHERE spool_id = ?", (spool_id,))
    db.execute("DELETE FROM spools WHERE id = ?", (spool_id,))
    db.commit()
    return jsonify({"ok": True})
