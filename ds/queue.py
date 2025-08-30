from typing import Generic, List, TypeVar, Optional

T = TypeVar("T")

class Queue(Generic[T]):
    def __init__(self) -> None:
        self._a: List[T] = []
        self._h: int = 0

    def __len__(self) -> int:
        return len(self._a) - self._h
    
    def enqueue(self, x: T) -> None:
        self._a.append(x)

    def dequeue(self) -> Optional[T]:
        if self._h == len(self._a):
            return None
        x = self._a[self._h]
        self._h += 1
        #COMPACT
        if self._h > 32 and self._h * 2 > len(self._a):
            self._a = self._a[self._h:]
            self._h = 0
        return x
    
    def peek(self) -> Optional[T]:
        if self._h == len(self._a):
            return None
        return self._a[self._h]