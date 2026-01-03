from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser, NormalizedRecord
from normalizer.registry import BankRegistry

class WellsFargoParser(BankStatementParser):
  delimiter = ","
  has_header = False

  def parse_rows(self, rows):
    records = []
    for row in rows:
      record = NormalizedRecord(
        transaction_date=datetime.strptime(row[0], "%m/%d/%Y").date(),
        description=row[4],
        amount=Decimal(row[1]),
        raw=row,
      )
      self.validate(record)
      records.append(record)
    return records

BankRegistry.register("wells_fargo", WellsFargoParser)