from dataclasses import dataclass
from typing import Pattern
from .base import TransactionRecord, SubTransactionRecord

@dataclass(frozen=True)
class CategoryRule:
  pattern: Pattern[str]
  categories: list[str]
  protect_manual: bool

class Categorizer:
    def __init__(self, rules: list[CategoryRule]):
      self._rules = rules

    def categorize(
      self,
      memo: str,
      existing: str | None = None,
    ) -> str | None:
      for rule in self._rules:
        if rule.pattern.search(memo):
          if rule.protect_manual and existing:
            return existing
          return rule.categories[0]
      return existing
    
    def apply(
        self,
        record: SubTransactionRecord,
        description: str,
        existing: TransactionRecord | None,
    ) -> None:
        existing_category = existing.records[0].category if existing is not None and len(existing.records) == 1 else record.category

        new_category = self.categorize(
            description,
            existing=existing_category,
        )

        record.category = new_category