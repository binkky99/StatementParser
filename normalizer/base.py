from abc import abstractmethod
import hashlib
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Iterable, Optional
from .exceptions import ValidationError

@dataclass
class NormalizedRecord:
  bank: str
  transaction_date: date
  description: str
  amount: Decimal
  category: Optional[str] = None
  key: str = field(init=False)
  raw: dict | None = None
  member_name: Optional[str] = None

  def __post_init__(self) -> None:
    self.key = self._generate_key()
  
  def _generate_key(self) -> str:
    """
    Deterministic, stable record key.
    """
    payload = "|".join([
      self.bank.lower().strip(),
      self.transaction_date.isoformat(),
      self.description.strip().lower(),
      f"{self.amount:.2f}",
    ])

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
  
  def ensure_key(self) -> None:
    """
    Assign key if not already present.
    """
    if not self.key:
      self.key = self.generate_key()

class BankStatementParser:
  """
  Base class each bank must implement.
  """
  bank: str | None = None

  delimiter: str = ","
  has_header: bool = True

  @abstractmethod
  def parse_rows(self, rows: Iterable[dict | list[str]]) -> list[NormalizedRecord]:
    raise NotImplementedError
  
  def _record(
      self,
      *,
      transaction_date: date,
      description: str,
      amount: Decimal | None = None,
      member_name: str | None = None,
      raw: dict | None = None
  ) -> NormalizedRecord:
    return NormalizedRecord(
      bank=self.bank,
      transaction_date=transaction_date,
      description=description,
      amount=amount,
      member_name=member_name,
      raw=raw,
    )

  def validate(self, record: NormalizedRecord) -> None:
    if not isinstance(record.transaction_date, date):
      raise ValidationError("Invalid date")
    if not isinstance(record.amount, Decimal):
      raise ValidationError("Invalid amount")