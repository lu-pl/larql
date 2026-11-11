import itertools
from collections import Counter
from collections.abc import Iterator

import lark

from larql.exceptions import ValuesDuplicateVariableError, ValuesRowArityError


class ValuesClauseValidator(lark.Visitor):
    """Validator for duplicate variables and row arity in VALUES clauses.

    See SPARQL 1.2 Query Language, 19.7 Grammar, Notes 9 and 10:

       9. The number of variables in the variable list of a VALUES clause must
          correspond to the number of RDF terms in each of the lists of associated
          values in the DataBlock.

      10. Variables in the variable list of a VALUES clause must be unique within that list.

    Note that only [68] InlineDataFull needs checking; the grammar already
    constrains [67] InlineDataOneVar to a single variable and single values.
    """

    def inline_data_full(self, tree: lark.Tree) -> None:
        _check_unique_variables(tree=tree)
        _check_row_arities(tree=tree)


def _check_unique_variables(tree: lark.Tree) -> None:
    variables: list[str] = list(_get_variable_names(tree=tree))

    if duplicates := [
        variable for variable, count in Counter(variables).items() if count > 1
    ]:
        raise ValuesDuplicateVariableError(
            line=tree.meta.line, column=tree.meta.column, duplicates=duplicates
        )


def _get_variable_names(tree: lark.Tree) -> Iterator[str]:
    for child in tree.children:
        match child:
            case lark.Tree(data="var", children=[lark.Token(value=variable)]):
                yield variable.lstrip("?$")
            case _:  # not a variable
                continue


def _check_row_arities(tree: lark.Tree) -> None:
    variable_count: int = sum(1 for _ in _get_variable_names(tree=tree))

    for row_arity in _get_row_arities(tree=tree):
        if row_arity != variable_count:
            raise ValuesRowArityError(
                line=tree.meta.line,
                column=tree.meta.column,
                expected=variable_count,
                got=row_arity,
            )


def _get_row_arities(tree: lark.Tree) -> Iterator[int]:
    rows: Iterator[lark.Tree | lark.Token] = iter(
        tree.children[tree.children.index("{") + 1 : -1]
    )

    for child in rows:
        match child:
            case lark.Token(type="NIL"):
                yield 0
            case lark.Token(type="LPAR"):
                # count trees within LPAR and RPAR
                yield sum(
                    1
                    for _ in itertools.takewhile(
                        lambda value: isinstance(value, lark.Tree),
                        rows,
                    )
                )
            case _:  # pragma: no cover
                assert False, "This should never happen."
