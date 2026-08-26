"""
Data classes that could be used in config or style
"""
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float