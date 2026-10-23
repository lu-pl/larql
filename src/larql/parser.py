import textwrap
from importlib.resources import files

import lark

_grammar: str = (files("larql") / "sparql12.lark").read_text()
_lark_parser = lark.Lark(
    _grammar,
    parser="lalr",
    lexer="basic",
    keep_all_tokens=True,
)


class SPARQLParser:
    def __init__(self, sparql: str) -> None:
        self._sparql = sparql
        self._tree = _lark_parser.parse(sparql)

    def __repr__(self) -> str:
        indented_sparql: str = textwrap.indent(self._sparql.strip(), "  ")
        return f"{type(self).__name__}(\n{indented_sparql}\n)"

    def serialize(self) -> str:
        raise NotImplementedError
