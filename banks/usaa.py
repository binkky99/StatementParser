from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser, NormalizedRecord
from normalizer.registry import BankRegistry

class USAAParser(BankStatementParser):
  delimiter = ","
  has_header = True

  def parse_rows(self, rows):
    records = []
    for row in rows:
      record = NormalizedRecord(
        transaction_date=datetime.strptime(row["Date"], "%Y-%m-%d").date(),
        description=row["Original Description"],
        amount=Decimal(row["Amount"]),
        raw=row,
      )
      self.validate(record)
      records.append(record)
    return records

BankRegistry.register("usaa", USAAParser)