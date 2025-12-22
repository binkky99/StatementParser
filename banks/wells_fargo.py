from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser, NormalizedRecord
from normalizer.registry import BankRegistry

class WellsFargoParser(BankStatementParser):
  delimiter = ","
  has_header = True

def parse_rows(self, rows):
  records = []
  for row in rows:
    record = NormalizedRecord(
      transaction_date=datetime.strptime(row["Date"], "%m/%d/%Y").date(),
      description=row["Description"],
      amount=Decimal(row["Amount"]),
      balance=Decimal(row["Balance"]) if "Balance" in row else None,
      raw=row,
    )
    self.validate(record)
    records.append(record)
  return records

BankRegistry.register("wells_fargo", WellsFargoParser)