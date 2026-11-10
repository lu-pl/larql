from importlib.resources import files

import lark

from larql.exceptions import SPARQLSyntaxError
from larql.validators.codepoint_escapes import CodepointEscapeValidator
from larql.validators.dispatcher import ConstraintValidator
from larql.validators.values_clause import ValuesClauseValidator

_grammar: str = (files("larql") / "sparql12.lark").read_text()
_lark_parser = lark.Lark(
    _grammar,
    parser="lalr",
    lexer="basic",
    keep_all_tokens=True,
    propagate_positions=True,
)
_validator = ConstraintValidator(ValuesClauseValidator(), CodepointEscapeValidator())


def parse(sparql: str) -> lark.Tree:
    """Parse a SPARQL 1.2 string into a Lark parse tree.

    The string is first parsed against the SPARQL 1.2 grammar and the resulting tree
    is then checked for constraints the grammar cannot (easily) express.

    Note that all failures raise a `larql.exceptions.LarqlError` subclass:
    grammar violations raise `SPARQLSyntaxError`, constraint violations raise
    `SPARQLConstraintError` subclasses.
    """
    try:
        tree: lark.Tree = _lark_parser.parse(sparql)
    except lark.exceptions.UnexpectedInput as exc:
        raise SPARQLSyntaxError(
            line=exc.line,
            column=exc.column,
            context=exc.get_context(text=sparql),
        ) from exc

    return _validator.visit(tree=tree)
