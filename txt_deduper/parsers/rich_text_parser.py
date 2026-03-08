import os
from typing import Iterator
from docx import Document
import fitz  # PyMuPDF

class RichTextParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._is_pdf = self.file_path.lower().endswith('.pdf')
    
    def read_lines(self) -> Iterator[str]:
        if self._is_pdf:
            yield from self._read_pdf()
        else:
            yield from self._read_docx()

    def _read_pdf(self) -> Iterator[str]:
        doc = fitz.open(self.file_path)
        for page in doc:
            text = page.get_text("text")
            # PDF 的换行可能比较硬，按换行符拆分段落
            for line in text.split('\n'):
                stripped = line.strip()
                if stripped:
                    yield stripped
        doc.close()

    def _read_docx(self) -> Iterator[str]:
        doc = Document(self.file_path)
        for para in doc.paragraphs:
            stripped = para.text.strip()
            if stripped:
                yield stripped

    # 富文本强制转存 txt，不需要 write_lines 保存回 pdf/docx，而是直接交由 TextParser 去保存为 txt。
    def write_lines(self, lines: Iterator[str]) -> None:
        raise NotImplementedError("Rich text will be exported to TXT directly. Do not use write_lines here.")
