from datetime import datetime
from decimal import Decimal
from normalizer.base import BankStatementParser, NormalizedRecord
from normalizer.registry import BankRegistry

class CitiBankParser(BankStatementParser):
  delimiter = ","
  has_header = True

  def parse_rows(self, rows):
    raise NotImplementedError("Implement CitiBank mapping")


BankRegistry.register("citibank", CitiBankParser)