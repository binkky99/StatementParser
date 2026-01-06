from dataclasses import dataclass
import re
from typing import Pattern

class Categorizer:
  def __init__(self, rules: list[tuple[str, list[str]]]):
    self._compiled: list[tuple[Pattern[str], list[str]]] = [
      (re.compile(expr, re.IGNORECASE), categories)
      for expr, categories in rules
    ]

  def categorize(self, memo: str) -> list[str]:
    matches: list[str] = []

    for pattern, categories in self._compiled:
      if pattern.search(memo):
        matches.extend(categories)

    return matches