from typing import Iterator, List, Optional, Protocol

class Parser(Protocol):
    def read_lines(self) -> Iterator[str]:
        ...
    
    def write_lines(self, lines: Iterator[str]) -> None:
        ...
