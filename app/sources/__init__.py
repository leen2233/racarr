from .readallcomics import ReadAllComics
from .test import Test

readallcomics = ReadAllComics() # initialize instance
test = Test()

default = "readallcomics"

__all__ = [
    "readallcomics",
    "test"
]
