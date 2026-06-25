import json
from dataclasses import asdict, is_dataclass
from datetime import date
from decimal import Decimal

class TransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj) 
        if is_dataclass(obj):
            return asdict(obj)
        return super().default(obj)