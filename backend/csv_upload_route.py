# backend/csv_upload_route.py
"""
CSV Upload & Dataset API Blueprint
-----------------------------------
Provides endpoints for dynamic CSV upload, dataset management,
and analytics generation for the Teacher Analytics Dashboard.
"""

import io
import json
import uuid
import pandas as pd
from flask import Blueprint, request, jsonify, session

from backend.smart_csv_parser import parse_csv
from backend.analytics_engine import get_full_analytics
from backend.database import (
    create_upload, update_upload_meta, insert_dataset_records,
    get_uploads_for_session, get_dataset_records, delete_upload,
    get_db,
)

# Also keep legacy import for backward compat
try:
    from auto_process_csv import clear_and_reload
except ImportError:
    clear_and_reload = None

csv_bp = Blueprint("csv_upload", __name__, url_prefix="/api")


# ── Ensure upload session ID exists ─────────────────────────────────────────
def _get_session_id():
    """Get or create a session ID for tracking uploads."""
    if "upload_session_id" not in session:
        session["upload_session_id"] = uuid.uuid4().hex
    return session["upload_session_id"]


# ──────────────────────────────────────────────────────────────────────────────
# 1. UPLOAD CSV (new dynamic flow)
# ──────────────────────────────────────────────────────────────────────────────
@csv_bp.route("/upload-csv", methods=["POST"])
def upload_csv():
    """
    Accept a CSV file, parse it with smart detection, store records,
    and return upload summary + initial analytics.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request. Use field name 'file'."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only .csv files are accepted."}), 400

    # Read file content
    try:
        raw = file.stream.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return jsonify({"error": f"Could not read file: {e}"}), 400

    # Parse with smart CSV parser
    result = parse_csv(raw, filename=file.filename)

    if not result.success:
        return jsonify({
            "success": False,
            "errors": result.errors,
            "warnings": result.warnings,
        }), 400

    # Create upload record
    sess_id = _get_session_id()
    upload_id = create_upload(sess_id, file.filename)

    # Store records in database
    insert_dataset_records(upload_id, result.records)

    # Update upload metadata
    update_upload_meta(upload_id, result.row_count, result.column_mapping, result.warnings)

    # Generate analytics
    analytics = get_full_analytics(result.df)

    return jsonify({
        "success": True,
        "upload_id": upload_id,
        "filename": file.filename,
        "parse_summary": {
            **result.to_dict(),
            "filename": file.filename,
            "records": result.records,          # list of dicts for the table
        },
        "analytics": analytics,
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# 2. LIST DATASETS
# ──────────────────────────────────────────────────────────────────────────────
@csv_bp.route("/datasets", methods=["GET"])
def list_datasets():
    """List all uploads for the current session."""
    sess_id = _get_session_id()
    uploads = get_uploads_for_session(sess_id)
    return jsonify(uploads)


# ──────────────────────────────────────────────────────────────────────────────
# 3. GET DATASET DATA (paginated)
# ──────────────────────────────────────────────────────────────────────────────
@csv_bp.route("/dataset/<int:upload_id>/data", methods=["GET"])
def get_dataset_data(upload_id):
    """Get raw data for a dataset, with optional pagination."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    search = request.args.get("search", "").strip().lower()
    sort_by = request.args.get("sort_by", "student_name")
    sort_dir = request.args.get("sort_dir", "asc")

    records = get_dataset_records(upload_id)
    if not records:
        return jsonify({"error": "Dataset not found or empty."}), 404

    # Search filter
    if search:
        records = [r for r in records if
                   search in (r.get("student_name") or "").lower() or
                   search in (r.get("subject") or "").lower() or
                   search in (r.get("usn") or "").lower()]

    # Sort
    reverse = sort_dir == "desc"
    try:
        records.sort(key=lambda x: (x.get(sort_by) or ""), reverse=reverse)
    except Exception:
        pass

    total = len(records)
    start = (page - 1) * per_page
    end = start + per_page
    page_records = records[start:end]

    return jsonify({
        "records": page_records,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    })


# ──────────────────────────────────────────────────────────────────────────────
# 4. GET ANALYTICS FOR A DATASET
# ──────────────────────────────────────────────────────────────────────────────
@csv_bp.route("/dataset/<int:upload_id>/analytics", methods=["GET"])
def get_dataset_analytics(upload_id):
    """Generate full analytics for a stored dataset."""
    records = get_dataset_records(upload_id)
    if not records:
        return jsonify({"error": "Dataset not found."}), 404

    df = pd.DataFrame(records)
    analytics = get_full_analytics(df)
    return jsonify(analytics)


# ──────────────────────────────────────────────────────────────────────────────
# 5. DELETE A DATASET
# ──────────────────────────────────────────────────────────────────────────────
@csv_bp.route("/dataset/<int:upload_id>", methods=["DELETE"])
def delete_dataset(upload_id):
    """Delete an upload and all its records."""
    delete_upload(upload_id)
    return jsonify({"message": "Dataset deleted successfully."})


# ──────────────────────────────────────────────────────────────────────────────
# 6. EXPORT DATASET REPORT
# ──────────────────────────────────────────────────────────────────────────────
@csv_bp.route("/dataset/<int:upload_id>/export", methods=["GET"])
def export_dataset(upload_id):
    """Export dataset records as CSV."""
    records = get_dataset_records(upload_id)
    if not records:
        return jsonify({"error": "Dataset not found."}), 404

    df = pd.DataFrame(records)
    # Remove internal ID columns
    for col in ["id", "upload_id"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    csv_str = df.to_csv(index=False)
    from flask import Response
    return Response(
        csv_str,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{upload_id}.csv"}
    )
