from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Optional
from .exceptions import ValidationError

@dataclass
class NormalizedRecord:
  transaction_date: date
  description: str
  amount: Decimal
  category: Optional[str] = None
  raw: dict | None = None

class BankStatementParser:
  """
  Base class each bank must implement.
  """
  delimiter: str = ","
  has_header: bool = True

  def parse_rows(self, rows: Iterable[dict | list[str]]) -> list[NormalizedRecord]:
    raise NotImplementedError

  def validate(self, record: NormalizedRecord) -> None:
    if not isinstance(record.transaction_date, date):
      raise ValidationError("Invalid date")
    if not isinstance(record.amount, Decimal):
      raise ValidationError("Invalid amount")