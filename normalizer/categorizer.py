import re
from typing import Pattern

class Categorizer:
  def __init__(self, rules: dict[str, str]):
    # category -> regex
    self._compiled: list[tuple[str, Pattern[str]]] = [
      (cat, re.compile(expr, re.IGNORECASE)) for cat, expr in rules.items()
    ]

  def categorize(self, memo: str) -> str | None:
    for category, pattern in self._compiled:
      if pattern.search(memo):
        return category
    return None