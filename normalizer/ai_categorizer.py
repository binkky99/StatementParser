import json
import time
from encoders.TransactionEncoder import TransactionEncoder
from openai import OpenAI
from pydantic import BaseModel

class Category(BaseModel):
  key: str
  confidence: int
  category: str

class Categories(BaseModel):
  categories: list[Category]

BATCH_SIZE = 10

system_prompt = """
You assign budget categories to bank transactions.

You will receive a list of transactions containing:
- key
- memo
- amount
- purchaser (optional)

Assign exactly one category to each transaction.

Valid categories:
{}

Rules:
- Transactions containing the word "Gas" should be assigned to the Gas category.
- Restaurant purchases should be assigned to a Fun category when one exists.

Return only valid JSON matching this schema:

{{
  "categories": [
    {{
      "key": "identifier",
      "confidence": "Your confidence you correctly categorized this item (0-10 score)"
      "category": "Category Name"
    }}
  ]
}}

The number of output entries must exactly match the number of input transactions.
Do not include explanations, markdown, comments, or any text outside the JSON.
"""

categories = [
  "Grocery",
  "Gas",
  "Outing",
  "Other",
  "Fun - Tessa",
  "Fun - Chris",
  "Fun - Us",
  "Travel",
  "Maintenance",
  "Gifts",
  "Health/Wellness",
  "Household/Furniture",
  "Trash",
  "Water + Recycling",
  "Electric + Gas",
  "Mortgage",
  "Roth IRA",
  "Auto Insurance/Tax",
  "Internet",
  "A/C Loan",
  "Student Loan",
  "Phone",
  "Subscriptions",
  "Tithe",
  "Saving",
  "Income - Salary",
  "Income - Other",
  "Income - Rewards",
  "Income - Tax",
]

def generate_category(records: list) -> list[Category]:
  mapped_records = []
  for record in records:
    r_dict = { "key": record.key, "memo": record.description, "amount": record.amount, "member": record.member_name }
    mapped_records.append(json.dumps(r_dict, cls=TransactionEncoder))

  input_tokens: int = 0
  output_tokens: int = 0
  total_tokens: int = 0
  output = []

  start = time.perf_counter()

  for i in range(0, len(mapped_records), BATCH_SIZE):
    batch_records = mapped_records[i:i + BATCH_SIZE]

    client = OpenAI(
      base_url="http://localhost:11434/v1",
      api_key="ollama"
    )

    response = client.responses.parse(
      model="gemma4:e4b",
      input=[
        {
          "role": "system",
          "content": system_prompt.format("- \n".join(categories))
        },
        {
          "role": "user",
          "content": "\n".join(batch_records)
        }
      ],
      text_format=Categories,
      temperature=0.0
    )

    batch_input_tokens = response.usage.input_tokens
    batch_output_tokens = response.usage.output_tokens
    batch_total_tokens = response.usage.total_tokens
    input_tokens += batch_input_tokens
    output_tokens += batch_output_tokens
    total_tokens += batch_total_tokens

    for entry in response.output_parsed.categories:
      output.append(entry)

    print(f"Batch Prompt tokens: {batch_input_tokens}")
    print(f"Batch Completion tokens: {batch_output_tokens}")
    print(f"Batch Total tokens: {batch_total_tokens}\n========= completed {i + len(batch_records)}/{len(records)} ============\n\n")

  elapsed = time.perf_counter() - start

  print(f"Total Input tokens: {input_tokens}")
  print(f"Total Output tokens: {output_tokens}")
  print(f"Total tokens: {total_tokens}")
  print(f"Elapsed time: {elapsed:.3f} seconds")

  return output