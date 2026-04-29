from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser, TransactionRecord, SubTransactionRecord
from normalizer.registry import BankRegistry

class NormalizedParser(BankStatementParser):
  bank = "norm"

  delimiter = "\t"
  has_header = True

  def parse_rows(self, rows):
    records_by_ref: dict[str, list[list[str]]] = {}
    records = []
    
    for row in rows:
      date = datetime.strptime(
          row["transaction_date"], "%Y-%m-%d"
        ).date()
      key = row.get("key") if "key" in row else TransactionRecord.generate_key(row.get("bank"), date, row.get("description"), Decimal(row.get("amount")))

      if key is not None and key in records_by_ref:
        records_by_ref.get(key).append(row)
      else:
        records_by_ref[key] = list([row])

    for value in records_by_ref.values():
      first = value[0]
      amount = sum(Decimal(entry["amount"]) for entry in value)

      record = self._record(
        transaction_date=datetime.strptime(
          first["transaction_date"], "%Y-%m-%d"
        ).date(),
        description=first["description"],
        amount=amount,
        bank=first["bank"],
        member_name=first["member_name"],
        records=[SubTransactionRecord(Decimal(entry["amount"]), entry["category"], entry) for entry in value],
        raw=row,
      )
      self.validate(record)
      records.append(record)

    return records

BankRegistry.register(NormalizedParser.bank, NormalizedParser)