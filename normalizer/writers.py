import csv
from pathlib import Path
from typing import Iterable
from .base import NormalizedRecord

def write_csv(
  path: Path, 
  records: Iterable[NormalizedRecord],
  append: bool = False
) -> None:
  write_header = not path.exists() or not append
  
  mode = "a" if append else "w"

  with path.open(mode, newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    if write_header:
      writer.writerow([
        "bank",
        "transaction_date",
        "description",
        "amount",
        "category",
      ])

    for r in records:
      writer.writerow([
        r.bank,
        r.transaction_date.isoformat(),
        r.description,
        str(r.amount),
        r.category or "",
      ])