"""Safe serialization primitives for approved student-data exports.

This module intentionally does not query the database, authorise staff, or
create download links. Callers must enforce those controls before serialization.
"""
import csv
import io
import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


class ExportSerializationError(ValueError):
    pass


def _json_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (UUID, Decimal)):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ExportSerializationError("Export object keys must be strings.")
        return {key: _json_value(item) for key, item in value.items()}
    raise ExportSerializationError("Unsupported value in export record.")


def _csv_safe(value):
    """Neutralise spreadsheet formula prefixes without changing normal text."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(_json_value(value), ensure_ascii=False, sort_keys=True)
    elif isinstance(value, (datetime, date)):
        value = value.isoformat()
    elif isinstance(value, (UUID, Decimal)):
        value = str(value)
    elif not isinstance(value, (str, int, float, bool)):
        raise ExportSerializationError("Unsupported value in export record.")
    text = str(value)
    # Excel/LibreOffice may evaluate formulas after leading whitespace/control chars.
    probe = text.lstrip(" \t\r\n\x00")
    if probe.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def serialise_json(records, allowed_fields):
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        raise ExportSerializationError("Records must be a list of objects.")
    safe = [
        {key: _json_value(value) for key, value in row.items() if key in allowed_fields}
        for row in records
    ]
    return json.dumps(safe, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def serialise_csv(records, allowed_fields):
    if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
        raise ExportSerializationError("Records must be a list of objects.")
    fields = sorted({key for row in records for key in row if key in allowed_fields})
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    if fields:
        writer.writeheader()
        for row in records:
            writer.writerow({key: _csv_safe(row.get(key)) for key in fields})
    return output.getvalue()
