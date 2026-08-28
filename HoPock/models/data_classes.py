"""
Data classes that could be used in config or style
"""
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float

# kill this and use point
# @dataclass
# class Dim:
#     h: float
#     w: float