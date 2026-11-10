import itertools
from collections.abc import Iterator
from typing import cast

import lark

from larql.exceptions import AnnotatedPathError


class AnnotatedPathValidator(lark.Visitor):
    """Validator for reifiers and annotation blocks after complex property paths.

    See SPARQL 1.2 Query Language, 19.7 Grammar, Note 16:

        16. A reifier or annotation syntax is only permitted after a triple when
            the property position is a simple path (an IRI, the keyword a,
            or a variable), and not for other path expressions.

    The SPARQL 1.2 grammar does not express this constraint: [93] ObjectPath allows an
    AnnotationPath regardless of the verb, so every verb/object list pair in
    [89] PropertyListPathNotEmpty is checked here. Annotation blocks contain
    a PropertyListPathNotEmpty themselves, so nested annotations get visited as well.

    Also note that a parenthesized IRI, e.g. (:p), is a path expression
    and not a simple path.
    """

    def property_list_path_not_empty(self, tree: lark.Tree) -> None:
        # dropping all tokens (only ";" at this level) leaves
        # strictly alternating verbs and object lists
        verb_object_list_pairs = cast(
            Iterator[tuple[lark.Tree, lark.Tree]],  # cast for n=2
            itertools.batched(
                iterable=[
                    child for child in tree.children if isinstance(child, lark.Tree)
                ],
                n=2,
            ),
        )

        for verb, object_list in verb_object_list_pairs:
            if not _is_simple_path(verb=verb) and _has_annotation(
                object_list=object_list
            ):
                raise AnnotatedPathError(line=verb.meta.line, column=verb.meta.column)


def _is_simple_path(verb: lark.Tree) -> bool:
    # with keep_all_tokens=True, every path operator (/, |, ^, ?, +, *, !) and
    # parenthesis is a token, so a path is simple iff it consists of a single IRI or 'a'
    match verb:
        case lark.Tree(data="verb_simple"):
            return True
        case lark.Tree(data="verb_path"):
            match list(verb.scan_values(lambda _: True)):
                case [lark.Token(type="IRIREF" | "PNAME_LN" | "PNAME_NS" | "A")]:
                    return True
                case _:  # path expression
                    return False
        case _:  # pragma: no cover
            assert False, "This should never happen."


def _has_annotation(object_list: lark.Tree) -> bool:
    # dropping all tokens (only "," separating the objects at this level) leaves
    # the objects together with their annotations, i.e. the object_path trees
    return any(
        _is_annotated_object(object_path=child)
        for child in object_list.children
        if isinstance(child, lark.Tree)
    )


def _is_annotated_object(object_path: lark.Tree) -> bool:
    # only the object's own annotation counts, not annotations nested inside the
    # object, e.g. in a blank node property list; those belong to other verbs
    match object_path:
        case lark.Tree(
            data="object_path",
            children=[_, lark.Tree(data="annotation_path", children=annotations)],
        ):
            return bool(annotations)
        case _:  # pragma: no cover
            assert False, "This should never happen."
