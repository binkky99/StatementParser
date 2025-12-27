import csv
from pathlib import Path
from typing import Iterable

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