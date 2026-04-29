import csv
from pathlib import Path
from typing import Iterable
from .base import TransactionRecord

def write_statement(
  path: Path, 
  records: Iterable[TransactionRecord]
) -> None:
  with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")

    writer.writerow([
      "bank",
      "transaction_date",
      "description",
      "amount",
      "category",
      "member_name",
      "key"
    ])

    for r in records:
      for s in r.records:
        writer.writerow([
          r.bank,
          r.transaction_date.isoformat(),
          r.description,
          str(s.amount),
          s.category or "",
          r.member_name or "",
          r.key
        ])

def write_unmapped(
  path: Path, 
  records: Iterable[str],
) -> None:
  with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for r in records:
      writer.writerow([r])