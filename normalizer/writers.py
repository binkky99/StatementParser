import csv
from pathlib import Path
from typing import Iterable
from .base import NormalizedRecord

def write_statement(
  path: Path, 
  records: Iterable[NormalizedRecord]
) -> None:
  with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")

    writer.writerow([
      "key",
      "bank",
      "transaction_date",
      "description",
      "amount",
      "category",
      "member_name"
    ])

    for r in records:
      writer.writerow([
        r.key,
        r.bank,
        r.transaction_date.isoformat(),
        r.description,
        str(r.amount),
        r.category or "",
        r.member_name or "",
      ])

def write_unmapped(
  path: Path, 
  records: Iterable[str],
) -> None:
  with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for r in records:
      writer.writerow([r])