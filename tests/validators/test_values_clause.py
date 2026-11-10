from typing import NamedTuple

import pytest

from larql import parse
from larql.exceptions import ValuesClauseError


class ValuesClauseTestParameter(NamedTuple):
    query: str
    comment: str = ""


valid_params: list[ValuesClauseTestParameter] = [
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a ?b) { (1 2) (3 4) } }",
        comment="Arity is checked per row, not against the total value count.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES ?a { 1 2 } }",
        comment="The one-variable form takes single values without parentheses.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES ?a { } }",
        comment="The one-variable form may have no values.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a ?b) { (1 UNDEF) (UNDEF UNDEF) } }",
        comment="UNDEF counts as a value.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a ?b) { } }",
        comment="A variable list may have no rows.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES () { () () } }",
        comment="An empty variable list matches empty rows, all lexed as NIL.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES () { ( ) } }",
        comment="NIL allows white space between the parentheses.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES ( ) { (\n# comment\n) } }",
        comment="A comment makes an empty row lex as LPAR RPAR instead of NIL.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (\n# comment\n) { () } }",
        comment=(
            "A comment makes an empty variable list lex as LPAR RPAR instead of NIL."
        ),
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { ?s ?p ?o } VALUES (?s) { (1) (2) }",
        comment="A trailing VALUES clause is checked like an inline one.",
    ),
]

invalid_params: list[ValuesClauseTestParameter] = [
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a ?b) { (1) (2) } }",
        comment="The total value count matches, but each row is too short.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a ?b) { (1 2) (3) } }",
        comment="Only a later row is too short.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a ?b) { (1 2 3) } }",
        comment="The row is too long.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a) { () } }",
        comment="An empty row doesn't match a non-empty variable list.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES () { (1) } }",
        comment="A non-empty row doesn't match an empty variable list.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a ?a) { (1 1) } }",
        comment="The variable list contains a duplicate.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { VALUES (?a $a) { (1 1) } }",
        comment="?a and $a denote the same variable, so this is a duplicate.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { ?s ?p ?o } VALUES (?s) { (1 2) }",
        comment="A trailing VALUES clause is checked like an inline one.",
    ),
    ValuesClauseTestParameter(
        query="SELECT * WHERE { { SELECT * WHERE { VALUES (?a) { (1 2) } } } }",
        comment="A VALUES clause inside a sub-SELECT is checked too.",
    ),
]


@pytest.mark.parametrize("param", valid_params)
def test_values_clause_validator(param: ValuesClauseTestParameter) -> None:
    parse(sparql=param.query)


@pytest.mark.parametrize("param", invalid_params)
def test_values_clause_validator_sad_path(param: ValuesClauseTestParameter) -> None:
    with pytest.raises(ValuesClauseError):
        parse(sparql=param.query)
