"""Filtro de logs que oculta datos personales (Ley 29733, ISO 27701)."""

import logging
import re

PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"\b\d{11}\b"), "[ruc]"),
    (re.compile(r"\b\d{8}\b"), "[dni]"),
    (re.compile(r"\b9\d{8}\b"), "[telefono]"),
]


def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class RedactPIIFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(str(record.getMessage()))
        record.args = ()
        return True
