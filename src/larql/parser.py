"""Lark interface for the SPARQL 1.1 grammar."""

from importlib.resources import files
from pathlib import Path

import lark
from larql.utils.validators import UnicodeValidator


_package_path = Path(files("larql"))  # type: ignore
_grammar_file = _package_path / "sparql.lark"

_grammar = _grammar_file.read_text(encoding="utf-8")
sparql_parser = lark.Lark(_grammar)


class SPARQLParser:
    def __init__(self, query: str) -> None:
        self.query = query
        self.tree: lark.Tree = sparql_parser.parse(self.query)

        self._run_validators(UnicodeValidator())

    def _run_validators(self, *validators: lark.Visitor):
        """Run validators against the Tree component."""
        for validator in validators:
            validator.visit(self.tree)

    def serialize(self):
        """Run a lark.Transformer for SPARQL serialization."""
