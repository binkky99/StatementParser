import argparse
from pathlib import Path
from banks import register_all
from normalizer.base import NormalizedRecord
from normalizer.readers import CategoryMapReader, DelimitedFileReader
from normalizer.categorizer import Categorizer
from normalizer.registry import BankRegistry
from normalizer.writers import write_statement, write_unmapped
from normalizer.read_existing import load_existing_records

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
      description="Normalize bank statements into a standard CSV format"
    )

    parser.add_argument(
      "bank",
      help="Bank identifier (e.g. wells_fargo, citibank, usaa, norm)",
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
      "--categories",
      type=Path,
      help="Categories file that provides mapping from Description to Category",
    )

    parser.add_argument(
      "--credit",
      action='store_true',
      help="Categories file that provides mapping from Description to Category",
    )

    return parser.parse_args()

def run(bank: str, path: Path, categoryPath: Path, credit: bool):
  parser_cls = BankRegistry.get(bank)
  parser = parser_cls()

  rows = DelimitedFileReader(path, parser.delimiter, parser.has_header).read()
  if categoryPath is not None and categoryPath.exists():
    categoryRows = CategoryMapReader(categoryPath, '\t').read()
  else:
    categoryRows = dict()
  
  records = parser.parse_rows(rows)

  categorizer = Categorizer(categoryRows)
  unmapped = set()

  # post process of records.
  for r in records:
    categories = categorizer.categorize(r.description)
    r.category = categories[0] if categories else None
    if credit:
      r.amount = -1 * r.amount
    if r.category is None:
      unmapped.add(r.description)
  
  return records, unmapped

def merge_records(
    existing: dict[str, NormalizedRecord],
    incoming: list[NormalizedRecord],
) -> tuple[list[NormalizedRecord], int, int, int]:
    added = 0
    updated = 0

    for record in incoming:
      old = existing.get(record.key)

      if old is None:
        existing[record.key] = record
        added += 1
      elif old != record:
        existing[record.key] = record
        updated += 1

    return list(existing.values()), added, updated

if __name__ == "__main__":
  import sys
  args = parse_args()

  register_all()
  
  if args.output is not None:
    if not args.output.is_dir():
      print(f"Error: output path does not exist: {args.output}")
      sys.exit(2)
    output_dir = args.output
  else:
    output_dir = Path.cwd() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
  
  output_path = output_dir / "Normalized_Statement.txt"

  existing_records = load_existing_records(output_path)
  
  parsed_records, unmapped = run(args.bank, args.input, args.categories, args.credit)
  merged, added, replaced = merge_records(existing_records, parsed_records)

  write_statement(output_path, merged)

  added_count = added
  parsed_count = len(parsed_records)
  skipped_count = parsed_count - added_count

  print(f"Parsed records     : {parsed_count}")
  print(f"Added records      : {added}")
  print(f"Updated records    : {replaced}")
  if unmapped:
    print(f"Unmapped categories: {len(unmapped)}")
  print(f"Output file        : {output_path}")

  if unmapped:
    output_unmapped = output_dir / "Unmapped_Categories.txt"
    print(f"Unmapped file      : {output_unmapped}")
    write_unmapped(output_dir / "Unmapped_Categories.txt", sorted(unmapped))