import csv
from pathlib import Path
from typing import Iterable
from .base import NormalizedRecord

def write_csv(path: Path, records: Iterable[NormalizedRecord]) -> None:
  with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # header
    writer.writerow([
      "transaction_date",
      "description",
      "amount",
      "category",
    ])

    for r in records:
      writer.writerow([
        r.transaction_date.isoformat(),
        r.description,
        str(r.amount),
        r.category or "",
      ])