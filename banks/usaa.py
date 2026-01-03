from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser, NormalizedRecord
from normalizer.registry import BankRegistry

class USAAParser(BankStatementParser):
  delimiter = "\t"
  has_header = False

  def parse_rows(self, rows):
    raise NotImplementedError("Implement USAA mapping")

BankRegistry.register("usaa", USAAParser)