from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser
from normalizer.registry import BankRegistry

class NormalizedParser(BankStatementParser):
  bank = "norm"

  delimiter = "\t"
  has_header = True

  def parse_rows(self, rows):
    records = []
    for row in rows:
      record = self._record(
        transaction_date=datetime.strptime(
          row["transaction_date"], "%Y-%m-%d"
        ).date(),
        description=row["description"],
        amount=Decimal(row["amount"]),
        bank=row["bank"],
        category=row["category"],
        member_name=row["member_name"],
        raw=row,
      )
      self.validate(record)
      records.append(record)
    return records

BankRegistry.register(NormalizedParser.bank, NormalizedParser)