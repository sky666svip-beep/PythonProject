import os
from typing import Iterator, List

class TextParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_lines(self) -> Iterator[str]:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                yield line.rstrip('\n')

    def write_lines(self, lines: Iterator[str]) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")
