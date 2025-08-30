from typing import Generic, List, Tuple, TypeVar, Optional

K = TypeVar("K")
V = TypeVar("V")

class MinHeap(Generic[K, V]):
    def __init__(self) -> None:
        self._a: List[Tuple[K, V]] = []

    def __len__(self) -> int:
        return len(self._a)
    
    def _parent(self, i: int) -> int: return (i-1) // 2
    def _left(self, i: int) -> int: return 2 * i + 1
    def _right(self, i: int) -> int: return 2 * i + 2

    def swap(self, i: int, j: int) -> None:
        self._a[i], self._a[j] = self._a[j], self._a[i]

    def push(self, key: K, value: V) -> None:
        self._a.append((key, value))
        i = len(self._a) - 1
        while i > 0:
            p = self._parent(i)
            if self._a[i][0] < self._a[p][0]:
                self._swap(i, p)
                i = p
            else:
                break

    def pop(self) -> Optional[Tuple[K, V]]:
        if not self._a:
            return None
        last = len(self._a) - 1
        self._swap(0, last)
        item = self._a.pop()

        i = 0
        n = len(self._a)
        while True:
            l, r = self._left(i), self._right(i)
            smallest = i
            if l < n and self._a[l][0] < self._a[smallest][0]:
                smallest = l
            if r < n and self._a[r][0] < self._a[smallest][0]:
                smallest = r
            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break
        return item