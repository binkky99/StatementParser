from abc import abstractmethod
import hashlib
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Iterable, Optional
from .exceptions import ValidationError

@dataclass
class TransactionRecord:
  bank: str
  transaction_date: date
  amount: Decimal
  description: str
  member_name: Optional[str] = None
  records: list[SubTransactionRecord] = field(default_factory=list)
  raw: dict | None = field(default=None, compare=False)
  key: str = field(default=None)

  def __post_init__(self) -> None:
    if isinstance(self.member_name, str) and self.member_name.strip() == "":
        self.member_name = None
    if self.key is None:
      self.key = self.generate_key(
          self.bank, self.transaction_date, self.description, self.amount
      )

  @staticmethod
  def generate_key(bank: str, transaction_date: date, description: str, amount: Decimal) -> str:
      """
      Deterministic, stable record key.
      """
      payload = "|".join([
        bank.lower().strip(),
        transaction_date.isoformat(),
        description.lower(),
        f"{abs(amount):.2f}",
      ])

      return hashlib.sha256(payload.encode("utf-8")).hexdigest()

@dataclass
class SubTransactionRecord:
  amount: Decimal
  category: Optional[str] = None
  raw: dict | None = field(default=None, compare=False)

  def __post_init__(self) -> None:
    if isinstance(self.category, str) and self.category.strip() == "":
        self.category = None


class BankStatementParser:
  """
  Base class each bank must implement.
  """
  bank: str | None = None

  credit: bool = False
  delimiter: str = ","
  has_header: bool = True

  @abstractmethod
  def parse_rows(self, rows: Iterable[dict | list[str]]) -> list[TransactionRecord]:
    raise NotImplementedError
  
  def _record(
      self,
      *,
      transaction_date: date,
      description: str,
      amount: Decimal | None = None,
      bank: str | None = None,
      member_name: str | None = None,
      records: list[SubTransactionRecord] = None,
      raw: dict | None = None
  ) -> TransactionRecord:
    amount=amount if not self.credit else amount * -1
    if records is None:
      records = [SubTransactionRecord(amount)]

    return TransactionRecord(
      bank=bank if bank is not None else self.bank,
      transaction_date=transaction_date,
      description=description,
      amount=amount,
      member_name=member_name,
      records=records,
      raw=raw,
    )

  def validate(self, record: TransactionRecord) -> None:
    if not isinstance(record.transaction_date, date):
      raise ValidationError("Invalid date")
    if not isinstance(record.amount, Decimal):
      raise ValidationError("Invalid amount")