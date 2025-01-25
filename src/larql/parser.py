"""Lark interface for the SPARQL 1.1 grammar."""

from importlib.resources import files
from pathlib import Path

from lark import Lark


_package_path = Path(files("larql"))  # type: ignore
_grammar_file = _package_path / "sparql.lark"
_grammar = _grammar_file.read_text()

sparql_parser = Lark(_grammar, start="query_unit")
