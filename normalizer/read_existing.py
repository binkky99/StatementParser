import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from .base import NormalizedRecord

def load_existing_keys(path: Path) -> set[str]:
  if not path.exists():
    return set()

  keys = set()
  with path.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
      record = NormalizedRecord(
        row["bank"],
        datetime.strptime(
          row["transaction_date"], "%Y-%m-%d"
        ).date(),
        row["description"],
        Decimal(row["amount"])
      )
      keys.add(record.key)
  return keys