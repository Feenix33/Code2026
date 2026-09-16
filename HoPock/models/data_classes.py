"""
Data classes that could be used in config or style
"""
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Token:
    kind: Literal["command", "text"]
    name: str | None    # eg H1 BP
    args: list[str]     # command parameters
    text: str | None    # Raw text if kind == text