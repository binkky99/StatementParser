import csv
from pathlib import Path
from collections import defaultdict
from typing import Iterable

class CategoryMapReader:
  def __init__(self, path: Path, delimiter: str = ","):
    self.path = path
    self.delimiter = delimiter

  def read(self) -> list[tuple[str, list[str]]]:
    """
    Returns: [(regex, [category1, category2, ...]), ...]
    """
    rules: dict[str, list[str]] = defaultdict(list)

    with self.path.open(newline="", encoding="utf-8-sig") as f:
      reader = csv.DictReader(f, delimiter=self.delimiter)

      if not reader.fieldnames:
        raise ValueError("Category map file must have a header")

      required = {"category", "regex"}
      missing = required - set(reader.fieldnames)
      if missing:
        raise ValueError(f"Missing required columns: {missing}")

      for row in reader:
        category = row["category"].strip()
        regex = row["regex"].strip()

        if not category or not regex:
          continue  # or raise, depending on strictness

        rules[regex].append(category)

    return list(rules.items())

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
