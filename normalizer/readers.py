import csv
from .categorizer import CategoryRule
from pathlib import Path
import re
from typing import Iterable

class CategoryMapReader:
  def __init__(self, path: Path, delimiter: str = "\t"):
    self.path = path
    self.delimiter = delimiter

  def read(self) -> list[CategoryRule]:
    grouped: dict[str, dict] = {}

    with self.path.open(newline="", encoding="utf-8-sig") as f:
      reader = csv.DictReader(f, delimiter=self.delimiter)

      for row in reader:
        regex = row["regex"].strip()
        category = row["category"].strip()
        protect = (row.get("protect_manual") or "").strip().lower() == "true"

        if regex not in grouped:
          grouped[regex] = {
            "categories": [],
            "protect_manual": protect,
          }

        grouped[regex]["categories"].append(category)

    return [
      CategoryRule(
        pattern=re.compile(expr, re.IGNORECASE),
        categories=data["categories"],
        protect_manual=data["protect_manual"],
      )
      for expr, data in grouped.items()
    ]

class DelimitedFileReader:
  def __init__(self, path: Path, delimiter: str, has_header: bool):
    self.path = path
    self.delimiter = delimiter
    self.has_header = has_header

  def read(self) -> Iterable[dict | list[str]]:
    with self.path.open(newline="", encoding="utf-8-sig") as f:
      if self.has_header:
        reader = csv.DictReader(f, delimiter=self.delimiter)
        yield from reader
      else:
        reader = csv.reader(f, delimiter=self.delimiter)
        yield from reader
