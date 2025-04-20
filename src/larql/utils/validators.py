"""lark.Visitors for parse tree validation."""

import lark


class BindScopeValidator(lark.Visitor):
    """Validator for checking that bound variables are not previously used."""


class UnicodeValidator(lark.Visitor):
    """Validator for checking that string terminals are UTF-8 encodable."""

    def string(self, node):
        for child in node.children:
            try:
                child.encode("utf-8")
            except UnicodeEncodeError as e:
                message = (
                    "Invalid Unicode encoding in string literal: "
                    f"{child} (Reason: {e.reason})"
                )
                raise lark.ParseError(message) from e


class InsertDeleteQuadValidator(lark.Visitor):
    """Validator for checking semantic quad constraints in INSERT/DELETE environments."""

    def _validate_children(
        self, node: lark.Tree, disallowed: set[str], error_message
    ) -> None:
        for child in node.children:
            if isinstance(child, lark.Token):
                continue
            else:
                if child.data in disallowed:
                    message = error_message.format(child=child)
                    raise lark.ParseError(message)

                self._validate_children(child, disallowed, error_message)

    def insert_data(self, node: lark.Tree) -> None:
        message = "Variable nodes are not allowed in INSERT DATA. Found node '{child}'."
        self._validate_children(node, {"var"}, message)

    def delete_data(self, node: lark.Tree) -> None:
        message = "Variables and blank nodes are not allowed in DELETE DATA contexts. Found node: '{child}'."
        self._validate_children(node, {"var", "blank_node"}, message)

    def delete_clause(self, node: lark.Tree) -> None:
        message = (
            "Blank nodes are not allowed in DELETE clauses.\nFound node: '{child}'."
        )
        self._validate_children(node, {"blank_node"}, message)

    def delete_where(self, node: lark.Tree) -> None:
        message = (
            "Blank nodes are not allowed in DELETE WHERE contexts.\n"
            "Found node: '{child}'."
        )
        self._validate_children(node, {"blank_node"}, message)
