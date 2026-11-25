from collections.abc import Iterator

import lark

from larql.exceptions import DataVariableError


class DataVariableValidator(lark.Visitor):
    """Validator for variables in INSERT DATA and DELETE DATA operations.

    See SPARQL 1.2 Query Language, 19.7 Grammar, Note 6:

        6. The QuadData and QuadPattern rules both use rule Quads. The rule QuadData,
           used in INSERT DATA and DELETE DATA must not allow variables in the quad patterns.

    Note that [51] QuadData is only used by [40] InsertData and [41] DeleteData,
    so checking QuadData covers both. Every variable in the subtree is rejected,
    including graph names (GRAPH ?g), reifier ids and variables in triple terms.
    """

    def quad_data(self, tree: lark.Tree) -> None:
        variables: Iterator[lark.Tree] = filter(
            lambda subtree: subtree.data == "var", tree.iter_subtrees_topdown()
        )

        match next(variables, None):
            case None:
                return
            case lark.Tree(meta=meta, children=[lark.Token(value=variable)]):
                raise DataVariableError(
                    line=meta.line, column=meta.column, variable=variable
                )
            case _:  # pragma: no cover
                assert False, "This should never happen."
