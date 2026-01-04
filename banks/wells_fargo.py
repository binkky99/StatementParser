from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser
from normalizer.registry import BankRegistry

class WellsFargoParser(BankStatementParser):
  bank = "wells_fargo"

  delimiter = ","
  has_header = False

  def parse_rows(self, rows):
    records = []
    for row in rows:
      record = self._record(
        transaction_date=datetime.strptime(
          row[0], "%m/%d/%Y"
        ).date(),
        description=row[4],
        amount=Decimal(row[1]),
        raw=row,
      )
      self.validate(record)
      records.append(record)
    return records

BankRegistry.register(WellsFargoParser.bank, WellsFargoParser)