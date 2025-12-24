# filament_tracker/routes/usages.py
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime

from ..db import get_db

bp = Blueprint("usages", __name__)


@bp.route("/api/usages", methods=["POST"])
def api_usages_post():
    db = get_db()
    data = request.json or {}

    # spool validation
    try:
        spool_id = int(data["spool_id"])
    except (KeyError, ValueError):
        return jsonify({"error": "invalid spool_id"}), 400

    cur = db.execute("SELECT id FROM spools WHERE id = ?", (spool_id,))
    if not cur.fetchone():
        return jsonify({"error": "spool not found"}), 404

    used_grams = data.get("used_grams")
    if used_grams in (None, ""):
        return jsonify({"error": "used_grams required"}), 400

    try:
        used_grams = float(used_grams)
    except ValueError:
        return jsonify({"error": "invalid used_grams"}), 400

    if used_grams <= 0:
        return jsonify({"error": "used_grams must be > 0"}), 400

    note = data.get("note")

    db.execute(
        """
        INSERT INTO usages (spool_id,used_grams,used_length_m,note,created_at)
        VALUES (?,?,?,?,?)
        """,
        (
            spool_id,
            used_grams,
            None,
            note,
            datetime.now(current_app.config["TZ"]).isoformat(),
        ),
    )
    db.commit()
    return jsonify({"ok": True}), 201


@bp.route("/api/usages/<int:spool_id>", methods=["GET"])
def api_usages_get(spool_id):
    db = get_db()
    cur = db.execute(
        "SELECT * FROM usages WHERE spool_id = ? ORDER BY created_at DESC",
        (spool_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)


@bp.route("/api/usage/<int:usage_id>", methods=["GET", "PUT", "DELETE"])
def api_usage(usage_id):
    db = get_db()
    cur = db.execute("SELECT * FROM usages WHERE id = ?", (usage_id,))
    usage = cur.fetchone()
    if not usage:
        return jsonify({"error": "not found"}), 404

    if request.method == "GET":
        return jsonify(dict(usage))

    if request.method == "DELETE":
        db.execute("DELETE FROM usages WHERE id = ?", (usage_id,))
        db.commit()
        return jsonify({"ok": True})

    # PUT: eidt usage history
    data = request.json or {}
    used_grams = data.get("used_grams")
    note = data.get("note") if "note" in data else usage["note"]

    # 只改备注
    if used_grams in (None, ""):
        db.execute(
            "UPDATE usages SET note=? WHERE id=?",
            (note, usage_id),
        )
        db.commit()
        return jsonify({"ok": True})

    try:
        used_grams = float(used_grams)
    except ValueError:
        return jsonify({"error": "invalid used_grams"}), 400

    if used_grams <= 0:
        return jsonify({"error": "used_grams must be > 0"}), 400

    db.execute(
        "UPDATE usages SET used_grams=?, note=? WHERE id=?",
        (used_grams, note, usage_id),
    )
    db.commit()
    return jsonify({"ok": True})
