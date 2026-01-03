from typing import Type
from .base import BankStatementParser

class BankRegistry:
  _parsers: dict[str, Type[BankStatementParser]] = {}

  @classmethod
  def register(cls, name: str, parser: Type[BankStatementParser]):
    cls._parsers[name.lower()] = parser

  @classmethod
  def get(cls, name: str) -> Type[BankStatementParser]:
    return cls._parsers[name.lower()]