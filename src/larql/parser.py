from importlib.resources import files

import lark

from larql.validators.dispatcher import SemanticConstraintValidator
from larql.validators.values_clause import ValuesClauseValidator

_grammar: str = (files("larql") / "sparql12.lark").read_text()
_lark_parser = lark.Lark(
    _grammar,
    parser="lalr",
    lexer="basic",
    keep_all_tokens=True,
    propagate_positions=True,
)
_validator = SemanticConstraintValidator(ValuesClauseValidator())


def parse(sparql: str) -> lark.Tree:
    """Parse a SPARQL 1.2 string into a Lark parse tree.

    The string is first parsed against the SPARQL 1.2 grammar and the resulting tree
    is then checked for semantic constraints the grammar cannot (easily) express.

    Note that all failures raise a `lark.exceptions.LarkError` subclass: grammar
    violations raise Lark's own exceptions, semantic violations raise
    `larql.exceptions.SemanticConstraintError` subclasses.
    """
    return _validator.visit(tree=_lark_parser.parse(sparql))
