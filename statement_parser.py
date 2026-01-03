from pathlib import Path
from banks import register_all
from normalizer.readers import DelimitedFileReader
from normalizer.categorizer import Categorizer
from normalizer.registry import BankRegistry
from normalizer.writers import write_csv

CATEGORY_RULES = {
  # "Groceries": r"whole foods|trader joe",
}

def run(bank: str, path: Path):
  print(BankRegistry._parsers)
  parser_cls = BankRegistry.get(bank)
  parser = parser_cls()
  print(type(parser))
  print(parser.__class__.__mro__)

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
  register_all()
  
  bank = sys.argv[1]
  input_path = Path(sys.argv[2])

  output_path = (
      input_path.with_suffix("")  # remove .csv / .txt
      .with_name(input_path.stem + "_normalized.csv")
  )

  recs, unmapped = run(bank, input_path)

  write_csv(output_path, recs)

  print(f"Parsed {len(recs)} records")
  if unmapped:
    print("Unmapped descriptions:")
  for u in sorted(unmapped):
    print(" -", u)