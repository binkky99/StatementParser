from dataclasses import dataclass
from typing import Pattern
from .base import NormalizedRecord

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
        record: NormalizedRecord,
        existing: NormalizedRecord | None,
    ) -> None:
        existing_category = existing.category if existing else record.category

        new_category = self.categorize(
            record.description,
            existing=existing_category,
        )

        record.category = new_category