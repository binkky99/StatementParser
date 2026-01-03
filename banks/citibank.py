from datetime import datetime
from decimal import Decimal, InvalidOperation
from normalizer.base import BankStatementParser, NormalizedRecord
from normalizer.registry import BankRegistry

class CitiBankParser(BankStatementParser):
  delimiter = ","
  has_header = True

  def parse_rows(self, rows):
    records = []
    for row in rows:
      try:
        amount=Decimal(row["Debit"])
      except InvalidOperation:
        continue

      record = NormalizedRecord(
        transaction_date=datetime.strptime(row["Date"], "%m/%d/%Y").date(),
        description=row["Description"],
        amount=amount,
        member_name=row["Member Name"],
        raw=row,
      )
      self.validate(record)
      records.append(record)
    return records

BankRegistry.register("citibank", CitiBankParser)