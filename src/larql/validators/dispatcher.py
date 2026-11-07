from typing import Protocol

import lark


class SupportsVisit(Protocol):
    """Structural type for objects that traverse a parse tree via `visit`.

    Note that this is intended to cover `lark.Visitor`, `lark.visitors.Visitor_Recursive`
    and `lark.visitors.Interpreter`, which share no useful Lark base class.

    The return type is `object` and not `lark.Tree` because `Interpreter.visit`
    returns whatever its handlers produce.
    """

    def visit(self, tree: lark.Tree) -> object: ...


class SemanticConstraintValidator(SupportsVisit):
    """Dispatcher for running validators over a parse tree.

    Note that validators run in the given order and each one traverses the tree;
    the first validator that raises stops the entire validation process.
    """

    def __init__(self, *validators: SupportsVisit) -> None:
        self._validators = validators

    def visit(self, tree: lark.Tree) -> lark.Tree:
        for validator in self._validators:
            validator.visit(tree=tree)

        return tree
