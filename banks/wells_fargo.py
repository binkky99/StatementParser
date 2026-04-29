from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser
from normalizer.registry import BankRegistry

class WellsFargoParser(BankStatementParser):
  bank = "wells_fargo"

  delimiter = ","
  has_header = True

  def parse_rows(self, rows):
    records = []
    for row in rows:
      record = self._record(
        transaction_date=datetime.strptime(
          row["DATE"], "%m/%d/%Y"
        ).date(),
        description=row["DESCRIPTION"],
        amount=Decimal(row["AMOUNT"]),
        raw=row,
      )
      self.validate(record)
      records.append(record)
    return records

BankRegistry.register(WellsFargoParser.bank, WellsFargoParser)