from typing import NamedTuple

import pytest

from larql import AnnotatedPathError, parse


class AnnotatedPathTestParameter(NamedTuple):
    query: str
    comment: str = ""


valid_params: list[AnnotatedPathTestParameter] = [
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p ?o ~ :r }",
        comment="A prefixed name is a simple path.",
    ),
    AnnotatedPathTestParameter(
        query="SELECT * WHERE { ?s <x:p> ?o ~ <x:r> }",
        comment="An IRIREF is a simple path.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s : ?o ~ :r }",
        comment="A bare prefix (PNAME_NS) is a simple path.",
    ),
    AnnotatedPathTestParameter(
        query="SELECT * WHERE { ?s a ?o {| ?a ?b |} }",
        comment="The keyword 'a' is a simple path.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s ?p ?o ~ :r {| ?a ?b |} }",
        comment="A variable is a simple path.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p/:q ?o }",
        comment="Path expressions without annotations are valid.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p ?o ~ :r ; :q/:r ?x }",
        comment="Only the verb an annotation belongs to is checked.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p/:q [ :r ?x {| ?a ?b |} ] }",
        comment="Annotations nested inside an object belong to the inner verb.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p ?o {| :q/:r ?x |} }",
        comment="Path expressions inside annotation blocks are valid if unannotated.",
    ),
]

invalid_params: list[AnnotatedPathTestParameter] = [
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p/:q ?o ~ :r }",
        comment="Sequence paths can't take a reifier.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p|:q ?o {| ?a ?b |} }",
        comment="Alternative paths can't take an annotation block.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s ^:p ?o ~ :r }",
        comment="Inverse paths are path expressions.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p? ?o ~ :r }",
        comment="Path modifiers make a path expression.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s !:p ?o ~ :r }",
        comment="Negated property sets are path expressions.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s (:p) ?o ~ :r }",
        comment="A parenthesized IRI is a path expression, not an IRI.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p ?o ; :q/:r ?x, ?y ~ :r }",
        comment="Any object of a later pair in a property list is checked.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { ?s :p ?o {| :q* ?x ~ :r |} }",
        comment="Annotations inside annotation blocks are checked too.",
    ),
    AnnotatedPathTestParameter(
        query="PREFIX : <x:> SELECT * WHERE { << ?s :p ?o >> :q/:r ?x ~ :r }",
        comment="Reified triple subjects don't exempt the verb.",
    ),
]


@pytest.mark.parametrize("param", valid_params)
def test_annotated_path_validator(param: AnnotatedPathTestParameter) -> None:
    parse(sparql=param.query)


@pytest.mark.parametrize("param", invalid_params)
def test_annotated_path_validator_sad_path(
    param: AnnotatedPathTestParameter,
) -> None:
    with pytest.raises(AnnotatedPathError):
        parse(sparql=param.query)
