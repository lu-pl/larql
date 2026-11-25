from typing import NamedTuple

import pytest

from larql import DataVariableError, parse


class DataVariableTestParameter(NamedTuple):
    query: str
    comment: str = ""


valid_params: list[DataVariableTestParameter] = [
    DataVariableTestParameter(
        query="INSERT DATA { <x:s> <x:p> <x:o> }",
        comment="Ground triples are valid in INSERT DATA.",
    ),
    DataVariableTestParameter(
        query="DELETE DATA { GRAPH <x:g> { <x:s> <x:p> 'o' } }",
        comment="Ground quads are valid in DELETE DATA.",
    ),
    DataVariableTestParameter(
        query="INSERT DATA { <x:s> <x:p> <x:o> ~ <x:r> {| <x:q> 1 |} }",
        comment="Annotations with ground terms are valid.",
    ),
    DataVariableTestParameter(
        query="INSERT { ?s <x:p> ?o } WHERE { ?s <x:q> ?o }",
        comment="Variables in INSERT templates are not checked.",
    ),
    DataVariableTestParameter(
        query="DELETE { ?s <x:p> ?o } WHERE { ?s <x:p> ?o }",
        comment="Variables in DELETE templates are not checked.",
    ),
    DataVariableTestParameter(
        query="DELETE WHERE { ?s <x:p> ?o }",
        comment="Variables in DELETE WHERE are not checked.",
    ),
]

invalid_params: list[DataVariableTestParameter] = [
    DataVariableTestParameter(
        query="INSERT DATA { ?s <x:p> <x:o> }",
        comment="Variables can't be subjects in INSERT DATA.",
    ),
    DataVariableTestParameter(
        query="DELETE DATA { <x:s> ?p <x:o> }",
        comment="Variables can't be verbs in DELETE DATA.",
    ),
    DataVariableTestParameter(
        query="INSERT DATA { <x:s> <x:p> $o }",
        comment="Variables with a '$' prefix are variables too.",
    ),
    DataVariableTestParameter(
        query="INSERT DATA { GRAPH ?g { <x:s> <x:p> <x:o> } }",
        comment="Variables can't be graph names.",
    ),
    DataVariableTestParameter(
        query="INSERT DATA { <x:s> <x:p> <x:o> ~ ?r }",
        comment="Variables can't be reifier ids.",
    ),
    DataVariableTestParameter(
        query="INSERT DATA { <x:s> <x:p> <x:o> {| <x:q> ?x |} }",
        comment="Variables can't occur in annotation blocks.",
    ),
    DataVariableTestParameter(
        query="INSERT DATA { <x:s> <x:p> <<( ?s <x:p> <x:o> )>> }",
        comment="Variables can't occur in triple terms.",
    ),
    DataVariableTestParameter(
        query="INSERT DATA { <x:s> <x:p> [ <x:q> ( 1 ?x ) ] }",
        comment="Variables nested in blank node property lists and collections are found.",
    ),
    DataVariableTestParameter(
        query="INSERT DATA { <x:s> <x:p> <x:o> } ; DELETE DATA { ?s <x:p> <x:o> }",
        comment="Every operation in an update request is checked.",
    ),
]


class DataVariableLocationTestParameter(NamedTuple):
    query: str
    variable: str
    line: int
    column: int
    comment: str = ""


location_params: list[DataVariableLocationTestParameter] = [
    DataVariableLocationTestParameter(
        query="INSERT DATA { ?s ?p ?o }",
        variable="?s",
        line=1,
        column=15,
        comment="The first variable in document order is reported.",
    ),
    DataVariableLocationTestParameter(
        query="INSERT DATA { <x:s> <x:p> ?o ~ ?r }",
        variable="?o",
        line=1,
        column=27,
        comment="An object comes before its reifier id.",
    ),
    DataVariableLocationTestParameter(
        query="INSERT DATA { GRAPH ?g { ?s <x:p> <x:o> } }",
        variable="?g",
        line=1,
        column=21,
        comment="A graph name comes before the triples in its block.",
    ),
    DataVariableLocationTestParameter(
        query="INSERT DATA { <x:s> <x:p> [ <x:q> ?x ] ; <x:r> ?y }",
        variable="?x",
        line=1,
        column=35,
        comment="A nested variable comes before a later sibling's variable.",
    ),
    DataVariableLocationTestParameter(
        query="INSERT DATA {\n  <x:s> <x:p> <x:o> .\n  ?s <x:p> <x:o>\n}",
        variable="?s",
        line=3,
        column=3,
        comment="Lines are counted too.",
    ),
]


@pytest.mark.parametrize("param", valid_params)
def test_data_variable_validator(param: DataVariableTestParameter) -> None:
    parse(sparql=param.query)


@pytest.mark.parametrize("param", invalid_params)
def test_data_variable_validator_sad_path(param: DataVariableTestParameter) -> None:
    with pytest.raises(DataVariableError):
        parse(sparql=param.query)


@pytest.mark.parametrize("param", location_params)
def test_data_variable_validator_location(
    param: DataVariableLocationTestParameter,
) -> None:
    with pytest.raises(DataVariableError) as exc_info:
        parse(sparql=param.query)

    error: DataVariableError = exc_info.value
    assert (error.variable, error.line, error.column) == (
        param.variable,
        param.line,
        param.column,
    )
