import math
from decimal import Decimal
from datetime import date, datetime
import uuid


def to_json_safe(row_dict):
    """
    Recursively cleans a dictionary for Django JSONField.
    Converts dates/times to ISO strings and handles NaNs + UUIDs.
    """
    clean_dict = {}
    for k, v in row_dict.items():
        if isinstance(v, (date, datetime)):
            clean_dict[k] = v.isoformat()
        elif isinstance(v, Decimal):
            clean_dict[k] = str(v)
        elif isinstance(v, uuid.UUID):  # ✅ Handle UUID
            clean_dict[k] = str(v)
        elif isinstance(v, float) and math.isnan(v):
            clean_dict[k] = None
        elif isinstance(v, dict):  # 🔁 recursive for nested JSON
            clean_dict[k] = to_json_safe(v)
        elif isinstance(v, list):  # 🔁 handle lists too
            clean_dict[k] = [
                (
                    to_json_safe(item)
                    if isinstance(item, dict)
                    else str(item) if isinstance(item, uuid.UUID) else item
                )
                for item in v
            ]
        else:
            clean_dict[k] = v
    return clean_dict
