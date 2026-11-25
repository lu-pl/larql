import itertools
from collections.abc import Iterator

import lark

from larql.exceptions import DeleteBlankNodeError


class DeleteBlankNodeValidator(lark.Visitor):
    """Validator for blank node syntax in DELETE DATA, DELETE WHERE and DELETE templates.

    See SPARQL 1.2 Query Language, 19.7 Grammar, Note 7:

        7. Blank node syntax is not allowed in DELETE WHERE, the DeleteClause for DELETE,
           nor in DELETE DATA.

    Blank node syntax covers every construct that produces a blank node,
    not only blank node labels and []: blank node property lists, collections,
    reified triples without a reifier, '~' without a reifier id and annotation blocks
    not immediately preceded by a reifier all allocate fresh blank nodes
    (see SPARQL 1.2 Query Language, 4.3.1 and 4.3.2).

    Note that the WHERE clause of a DELETE operation is not part of
    [44] DeleteClause, so blank nodes in WHERE clauses are not affected.
    """

    def delete_data(self, tree: lark.Tree) -> None:
        _check_blank_node_syntax(tree=tree)

    def delete_where(self, tree: lark.Tree) -> None:
        _check_blank_node_syntax(tree=tree)

    def delete_clause(self, tree: lark.Tree) -> None:
        _check_blank_node_syntax(tree=tree)


def _check_blank_node_syntax(tree: lark.Tree) -> None:
    match next(_get_blank_node_syntax(tree=tree), None):
        case None:
            return
        case lark.Tree(meta=meta), syntax:
            raise DeleteBlankNodeError(
                line=meta.line, column=meta.column, syntax=syntax
            )
        case _:  # pragma: no cover
            assert False, "This should never happen."


def _get_blank_node_syntax(tree: lark.Tree) -> Iterator[tuple[lark.Tree, str]]:
    # yields in document order, except within an annotation: blocks are checked
    # at the annotation node, i.e. before earlier violations among its children
    for subtree in tree.iter_subtrees_topdown():
        match subtree:
            case lark.Tree(data="blank_node", children=[lark.Token(value=value)]):
                yield subtree, f"blank node '{value}'"
            case lark.Tree(data="blank_node_property_list"):
                yield subtree, "blank node property list"
            case lark.Tree(data="collection"):
                yield subtree, "collection"
            case lark.Tree(data="reifier", children=[lark.Token()]):
                yield subtree, "'~' without reifier id"
            # exactly '<<' subject verb object '>>', i.e. no reifier
            case lark.Tree(
                data="reified_triple",
                children=[lark.Token(value="<<"), _, _, _, lark.Token(value=">>")],
            ):
                yield subtree, "reified triple without reifier"
            case lark.Tree(data="annotation"):
                yield from (
                    (block, "annotation block without reifier")
                    for block in _get_implicitly_reified_annotation_blocks(
                        annotation=subtree
                    )
                )
            case _:
                continue


def _get_implicitly_reified_annotation_blocks(
    annotation: lark.Tree,
) -> Iterator[lark.Tree]:
    # annotation: (reifier | annotation_block)*
    # a block only uses a reifier that immediately precedes it;
    # without a preceding reifier, a block is reified implicitly with a fresh blank node
    for previous, current in itertools.pairwise([None, *annotation.children]):
        match previous, current:
            case lark.Tree(data="reifier"), _:
                continue
            case _, lark.Tree(data="annotation_block"):
                yield current
            case _:
                continue
