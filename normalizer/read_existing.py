from pathlib import Path
from .base import NormalizedRecord
from banks.normalized import NormalizedParser
from .readers import DelimitedFileReader

def load_existing_records(path: Path) -> dict[str, NormalizedRecord]:
    if not path.exists():
        return {}

    parser = NormalizedParser()
    reader = DelimitedFileReader(path, parser.delimiter, has_header=True)
    rows = reader.read()

    records = parser.parse_rows(rows)
    return {r.key: r for r in records}