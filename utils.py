import unicodedata
import hashlib
from decimal import Decimal, ROUND_DOWN

def canonicalize_record_input(record):
    # Accepts dict or Pydantic model
    data = record.dict() if hasattr(record, 'dict') else dict(record)
    return {
        'project_name': unicodedata.normalize('NFKC', data['project_name'].strip().lower()),
        'registry': unicodedata.normalize('NFKC', data['registry'].strip().lower()),
        'vintage': int(data['vintage']),
        'quantity': str(Decimal(data['quantity']).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)),
        'serial_number': unicodedata.normalize('NFKC', data['serial_number'].strip().lower()),
    }

def generate_record_id(canonical):
    # Deterministic hash of canonicalized fields - same input always gives same ID
    s = f"{canonical['project_name']}|{canonical['registry']}|{canonical['vintage']}|{canonical['quantity']}|{canonical['serial_number']}"
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
