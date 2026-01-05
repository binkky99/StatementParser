import argparse
from pathlib import Path
from banks import register_all
from normalizer.readers import DelimitedFileReader
from normalizer.categorizer import Categorizer
from normalizer.registry import BankRegistry
from normalizer.writers import write_csv
from normalizer.read_existing import load_existing_keys

CATEGORY_RULES = {
  # "Groceries": r"whole foods|trader joe",
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
      description="Normalize bank statements into a standard CSV format"
    )

    parser.add_argument(
      "bank",
      help="Bank identifier (e.g. wells_fargo, citibank, usaa)",
    )

    parser.add_argument(
      "input",
      type=Path,
      help="Input statement file (.csv or .tsv)",
    )

    parser.add_argument(
      "-o",
      "--output",
      type=Path,
      help="Output CSV path direcotry (default: ./output/normalized_statment.csv)",
    )

    parser.add_argument(
      "-c",
      "--categories"
      type=Path,
      help="Categories file that provides mapping from Description to Category",
    )

    return parser.parse_args()

def run(bank: str, path: Path, categoryPath: Path):
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
  args = parse_args()

  register_all()
  
  if args.output is not None:
    if not args.output.is_dir():
      print("Error: output path does not exist: {args.output}")
      sys.exit(2)
    output_dir = args.output
  else:
    output_dir = Path.cwd() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
  
  output_path = output_dir / "Normalized_Statement.txt"

  existing_keys = load_existing_keys(output_path)
  
  recs, unmapped = run(args.bank, args.input)
  new_records = []
  for r in recs:
    if r.key not in existing_keys:
      new_records.append(r)

  write_csv(output_path, new_records, append=True)

  added_count = len(new_records)
  parsed_count = len(recs)
  skipped_count = parsed_count - added_count

  print(f"Parsed records : {parsed_count}")
  print(f"Added records  : {added_count}")
  print(f"Skipped records: {skipped_count}")
  print(f"Output file    : {output_path}")

  # if unmapped:
  #   print("Unmapped descriptions:")
  #   for u in sorted(unmapped):
  #     print(" -", u)