from typing import NamedTuple

import pytest

from larql import DeleteBlankNodeError, parse


class DeleteBlankNodeTestParameter(NamedTuple):
    query: str
    comment: str = ""


class DeleteBlankNodeSyntaxTestParameter(NamedTuple):
    query: str
    syntax: str
    comment: str = ""


class DeleteBlankNodeLocationTestParameter(NamedTuple):
    query: str
    syntax: str
    line: int
    column: int
    comment: str = ""


valid_params: list[DeleteBlankNodeTestParameter] = [
    DeleteBlankNodeTestParameter(
        query="INSERT DATA { _:a <x:p> [ <x:q> ( 1 2 ) ] }",
        comment="Blank node syntax is valid in INSERT DATA.",
    ),
    DeleteBlankNodeTestParameter(
        query="INSERT DATA { <x:s> <x:p> <x:o> {| <x:q> 1 |} }",
        comment="Annotation blocks without reifier are valid in INSERT DATA.",
    ),
    DeleteBlankNodeTestParameter(
        query="INSERT { _:a <x:p> [] } WHERE { ?s ?p ?o }",
        comment="Blank node syntax is valid in INSERT templates.",
    ),
    DeleteBlankNodeTestParameter(
        query="DELETE { ?s <x:p> ?o } INSERT { ?s <x:q> [] } WHERE { ?s <x:p> ?o }",
        comment="The INSERT template of a DELETE/INSERT operation is not checked.",
    ),
    DeleteBlankNodeTestParameter(
        query="DELETE { ?s <x:p> ?o } WHERE { _:a <x:p> [ <x:q> ( ?o ) ] }",
        comment="Blank node syntax is valid in the WHERE clause of DELETE.",
    ),
    DeleteBlankNodeTestParameter(
        query="DELETE WHERE { ?s <x:p> ?o }",
        comment="DELETE WHERE without blank node syntax is valid.",
    ),
    DeleteBlankNodeTestParameter(
        query="DELETE { ?s <x:p> () } WHERE { ?s <x:p> ?o }",
        comment="The empty collection () is rdf:nil, not a blank node.",
    ),
    DeleteBlankNodeTestParameter(
        query="DELETE { ?s <x:p> ?o ~ ?r } WHERE { ?s <x:p> ?o }",
        comment="A variable reifier id is not a blank node.",
    ),
    DeleteBlankNodeTestParameter(
        query="DELETE { ?s <x:p> ?o ~ <x:r> {| <x:q> 1 |} } WHERE { ?s <x:p> ?o }",
        comment="Annotation blocks immediately preceded by a reifier use that reifier.",
    ),
    DeleteBlankNodeTestParameter(
        query=(
            "DELETE { ?s <x:p> ?o ~ <x:r1> {| <x:q> 1 |} ~ <x:r2> {| <x:q> 2 |} } "
            "WHERE { ?s <x:p> ?o }"
        ),
        comment="Every annotation block can have its own reifier.",
    ),
    DeleteBlankNodeTestParameter(
        query="DELETE { << ?s <x:p> ?o ~ <x:r> >> <x:q> 1 } WHERE { ?s <x:p> ?o }",
        comment="Reified triples with a reifier id are valid.",
    ),
    DeleteBlankNodeTestParameter(
        query="DELETE DATA { <x:s> <x:p> <<( <x:a> <x:b> <x:c> )>> }",
        comment="Triple terms don't allocate blank nodes.",
    ),
]

invalid_params: list[DeleteBlankNodeSyntaxTestParameter] = [
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE DATA { _:a <x:p> <x:o> }",
        syntax="blank node '_:a'",
        comment="Blank node labels are invalid in DELETE DATA.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE WHERE { ?s <x:p> [] }",
        syntax="blank node '[]'",
        comment="Anonymous blank nodes are invalid in DELETE WHERE.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE { ?s <x:p> [ <x:q> 1 ] } WHERE {}",
        syntax="blank node property list",
        comment="Blank node property lists are invalid in DELETE templates.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE { ?s <x:p> ( 1 2 ) } WHERE {}",
        syntax="collection",
        comment="Collections allocate a blank node per list cell.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE { ?s <x:p> ?o ~ } WHERE {}",
        syntax="'~' without reifier id",
        comment="'~' without reifier id allocates a blank node.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE { << ?s <x:p> ?o >> <x:q> 1 } WHERE {}",
        syntax="reified triple without reifier",
        comment="Reified triples without reifier allocate a blank node.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE { << ?s <x:p> ?o ~ >> <x:q> 1 } WHERE {}",
        syntax="'~' without reifier id",
        comment="Reified triples with '~' only allocate a blank node.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE { << << ?s <x:p> ?o >> <x:q> ?x ~ <x:r> >> <x:q> 1 } WHERE {}",
        syntax="reified triple without reifier",
        comment="Nested reified triples are checked too.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE { ?s <x:p> ?o {| <x:q> 1 |} } WHERE {}",
        syntax="annotation block without reifier",
        comment="Annotation blocks without reifier allocate a blank node.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE { ?s <x:p> ?o ~ <x:r> {| <x:q> 1 |} {| <x:q> 2 |} } WHERE {}",
        syntax="annotation block without reifier",
        comment="A reifier only applies to the immediately following annotation block.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE DATA { <x:s> <x:p> <<( _:b <x:p> <x:o> )>> }",
        syntax="blank node '_:b'",
        comment="Blank nodes in triple terms are blank node syntax.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE DATA { <x:s> <x:p> <x:o> ~ _:r }",
        syntax="blank node '_:r'",
        comment="Blank node reifier ids are blank node syntax.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="DELETE DATA { GRAPH <x:g> { _:a <x:p> <x:o> } }",
        syntax="blank node '_:a'",
        comment="Blank node syntax inside GRAPH blocks is checked.",
    ),
    DeleteBlankNodeSyntaxTestParameter(
        query="INSERT DATA { _:a <x:p> <x:o> } ; DELETE DATA { _:b <x:p> <x:o> }",
        syntax="blank node '_:b'",
        comment="Every operation in an update request is checked.",
    ),
]

location_params: list[DeleteBlankNodeLocationTestParameter] = [
    DeleteBlankNodeLocationTestParameter(
        query="DELETE { << _:a <x:p> ?o ~ >> <x:q> 1 } WHERE {}",
        syntax="blank node '_:a'",
        line=1,
        column=13,
        comment="A reified triple's subject comes before its reifier.",
    ),
    DeleteBlankNodeLocationTestParameter(
        query="DELETE { << ?s <x:p> ?o >> <x:q> [] } WHERE {}",
        syntax="reified triple without reifier",
        line=1,
        column=10,
        comment="A reified triple without reifier is reported at its '<<'.",
    ),
    DeleteBlankNodeLocationTestParameter(
        query="DELETE { ?s <x:p> ( [] 1 ) } WHERE {}",
        syntax="collection",
        line=1,
        column=19,
        comment="An outer construct comes before its contents.",
    ),
    DeleteBlankNodeLocationTestParameter(
        query="DELETE { ?s <x:p> ?o {| <x:q> [] |} } WHERE {}",
        syntax="annotation block without reifier",
        line=1,
        column=22,
        comment="An annotation block comes before its contents.",
    ),
    DeleteBlankNodeLocationTestParameter(
        query="DELETE { ?s <x:p> ?o ~ <x:r> {| <x:q> 1 |} {| <x:q> [] |} } WHERE {}",
        syntax="annotation block without reifier",
        line=1,
        column=44,
        comment="The second annotation block is reported, not the first.",
    ),
    DeleteBlankNodeLocationTestParameter(
        query="DELETE {\n  ?s <x:p> ?o .\n  ?s <x:q> []\n} WHERE {}",
        syntax="blank node '[]'",
        line=3,
        column=12,
        comment="Lines are counted too.",
    ),
]


@pytest.mark.parametrize("param", valid_params)
def test_delete_blank_node_validator(param: DeleteBlankNodeTestParameter) -> None:
    parse(sparql=param.query)


@pytest.mark.parametrize("param", invalid_params)
def test_delete_blank_node_validator_sad_path(
    param: DeleteBlankNodeSyntaxTestParameter,
) -> None:
    with pytest.raises(DeleteBlankNodeError) as exc_info:
        parse(sparql=param.query)

    assert exc_info.value.syntax == param.syntax


@pytest.mark.parametrize("param", location_params)
def test_delete_blank_node_validator_location(
    param: DeleteBlankNodeLocationTestParameter,
) -> None:
    with pytest.raises(DeleteBlankNodeError) as exc_info:
        parse(sparql=param.query)

    error: DeleteBlankNodeError = exc_info.value
    assert (error.syntax, error.line, error.column) == (
        param.syntax,
        param.line,
        param.column,
    )
