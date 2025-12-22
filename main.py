from pathlib import Path
from normalizer.readers import DelimitedFileReader
from normalizer.categorizer import Categorizer
from normalizer.registry import BankRegistry

CATEGORY_RULES = {
  # "Groceries": r"whole foods|trader joe",
}

def run(bank: str, path: Path):
  parser_cls = BankRegistry.get(bank)
  parser = parser_cls()

  reader = DelimitedFileReader(path, parser.delimiter, parser.has_header)
  rows = reader.read()

  records = parser.parse_rows(rows)

  categorizer = Categorizer(CATEGORY_RULES)
  unmapped = set()

  for r in records:
    r.category = categorizer.categorize(r.description)
    if r.category is None:
      unmapped.add(r.description)
  
  return records, unmapped

if __name__ == "__main__":
  import sys
  recs, unmapped = run(sys.argv[1], Path(sys.argv[2]))
  print(f"Parsed {len(recs)} records")
  if unmapped:
    print("Unmapped descriptions:")
  for u in sorted(unmapped):
    print(" -", u)