from typing import NotRequired, TypedDict, Unpack

class Animal(TypedDict):
    foo: int

    __extra__: str

    def __extra_field__(self, key: str) -> int:
        ...

animal = Animal({"foo": 10})
print(Animal.__required_keys__)
