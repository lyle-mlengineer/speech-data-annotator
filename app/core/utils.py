from uuid import UUID, uuid4
from typing import LiteralString


def generate_id(prefix: LiteralString = ["US", "TASK"]) -> str:
    raw_id: UUID = uuid4()
    id: str = f"{prefix}-{str(raw_id)}"
    return id