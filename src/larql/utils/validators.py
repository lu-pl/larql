"""lark.Visitors for parse tree validation."""

import lark


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


class GroupByValidator(lark.Visitor):
    pass
