from typing import NamedTuple

import pytest

from larql import CodepointEscapeError, parse


class CodepointEscapeTestParameter(NamedTuple):
    query: str
    comment: str = ""


valid_params: list[CodepointEscapeTestParameter] = [
    CodepointEscapeTestParameter(
        query=r'SELECT * WHERE { ?s ?p "\uD7FF\uE000\U0010FFFF" }',
        comment="The bounds around the surrogate range and the maximum are valid.",
    ),
    CodepointEscapeTestParameter(
        query=r'SELECT * WHERE { ?s ?p "\\uD800" }',
        comment="An escaped backslash followed by 'uD800' is not a numeric escape.",
    ),
    CodepointEscapeTestParameter(
        query=r'SELECT * WHERE { ?s ?p "\u005CuD800" }',
        comment="A code point produced by an escape is not scanned again.",
    ),
    CodepointEscapeTestParameter(
        query=r"SELECT * WHERE { ?s ?p <http://example/\u00E9\U0001F47E> }",
        comment="Numeric escapes of scalar values are valid in IRIs.",
    ),
]

invalid_params: list[CodepointEscapeTestParameter] = [
    CodepointEscapeTestParameter(
        query=r'SELECT * WHERE { ?s ?p "\uD800" }',
        comment="The lower bound of the surrogate range is invalid.",
    ),
    CodepointEscapeTestParameter(
        query=r'SELECT * WHERE { ?s ?p "\udfff" }',
        comment="The upper bound of the surrogate range is invalid in lowercase hex.",
    ),
    CodepointEscapeTestParameter(
        query=r'SELECT * WHERE { ?s ?p "\U0000D800" }',
        comment="Surrogates are invalid in the eight-digit form too.",
    ),
    CodepointEscapeTestParameter(
        query=r'SELECT * WHERE { ?s ?p "\U00110000" }',
        comment="Code points above U+10FFFF are invalid.",
    ),
    CodepointEscapeTestParameter(
        query=r'SELECT * WHERE { ?s ?p "\\\uD800" }',
        comment="An escaped backslash doesn't hide a following numeric escape.",
    ),
    CodepointEscapeTestParameter(
        query=r"SELECT * WHERE { ?s ?p '''\uD800''' }",
        comment="Long strings are checked too.",
    ),
    CodepointEscapeTestParameter(
        query=r"BASE <http://example/\uD800> SELECT * WHERE { ?s ?p ?o }",
        comment="IRIs in BASE declarations are checked too.",
    ),
    CodepointEscapeTestParameter(
        query=r"PREFIX ex: <http://example/\uD800> SELECT * WHERE { ?s ?p ?o }",
        comment="IRIs in PREFIX declarations are checked too.",
    ),
    CodepointEscapeTestParameter(
        query=r'VERSION "\uD800" SELECT * WHERE { ?s ?p ?o }',
        comment="Version specifiers are checked too.",
    ),
]


@pytest.mark.parametrize("param", valid_params)
def test_codepoint_escape_validator(param: CodepointEscapeTestParameter) -> None:
    parse(sparql=param.query)


@pytest.mark.parametrize("param", invalid_params)
def test_codepoint_escape_validator_sad_path(
    param: CodepointEscapeTestParameter,
) -> None:
    with pytest.raises(CodepointEscapeError):
        parse(sparql=param.query)
