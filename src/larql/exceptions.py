"""Larql exceptions.

All exceptions are subtypes of `LarkError`/`LarqlError`;
`SPARQLSyntaxError` indicates exceptions raised during `larql`'s parse step,
`SPARQLConstraintError` indicates exceptions raised during constraint checking.

lark.exceptions.LarkError
└── LarqlError
    ├── SPARQLSyntaxError(line, column, context)
    └── SPARQLConstraintError
        ├── ValuesClauseError
        │   ├── ValuesDuplicateVariableError(line, column, duplicates)
        │   └── ValuesRowArityError(line, column, expected, got)
        ├── CodepointEscapeError(line, column, escape)
        └── ...

Generally, subclasses take structured parameters, pass them unchanged
to `super().__init__` and compose their message in `__str__`.
This keeps `args` in line with the constructor signature,
which `copy` and `pickle` rely on to rebuild an exception as `cls(*args)`.
"""

import lark


class LarqlError(lark.exceptions.LarkError):
    """Base exception for all larql errors."""


class SPARQLSyntaxError(LarqlError):
    """Exception for indicating that a string does not conform to the SPARQL grammar.

    Note that `SPARQLSyntaxError` is used to wrap `lark.exceptions.UnexpectedInput`
    raised by the Lark parser; the original exception is available as `__cause__`.
    """

    def __init__(self, line: int, column: int, context: str) -> None:
        self.line = line
        self.column = column
        self.context = context

        super().__init__(line, column, context)

    def __str__(self) -> str:
        return (
            f"SPARQL syntax error at line {self.line}, column {self.column}:"
            f"\n\n{self.context}"
        )


class SPARQLConstraintError(LarqlError):
    """Base exception for violations of constraints the grammar cannot express.

    Simple LarqlError subclass that allows calling code
    to address non-local exits from `ConstraintValidator`.
    """


class ValuesClauseError(SPARQLConstraintError):
    """Base exception for constraint violations in VALUES clauses.

    Simple SPARQLConstraintError subclass that allows calling code
    to catch all VALUES clause violations at once.
    """


class ValuesDuplicateVariableError(ValuesClauseError):
    """Exception for indicating duplicate variables in VALUES clauses."""

    def __init__(self, line: int, column: int, duplicates: list[str]) -> None:
        self.line = line
        self.column = column
        self.duplicates = duplicates

        super().__init__(line, column, duplicates)

    def __str__(self) -> str:
        return (
            "Expected unique variables in VALUES clause "
            f"at line {self.line}, column {self.column}. "
            f"Got duplicates: {self.duplicates}."
        )


class ValuesRowArityError(ValuesClauseError):
    """Exception for indicating rows whose arity doesn't match the variable count in VALUES clauses."""

    def __init__(self, line: int, column: int, expected: int, got: int) -> None:
        self.line = line
        self.column = column
        self.expected = expected
        self.got = got

        super().__init__(line, column, expected, got)

    def __str__(self) -> str:
        return (
            f"Expected {self.expected} value(s) per row in VALUES clause "
            f"at line {self.line}, column {self.column}. "
            f"Got a row with {self.got}."
        )


class CodepointEscapeError(SPARQLConstraintError):
    """Exception for indicating numeric escape sequences that don't produce Unicode scalar values."""

    def __init__(self, line: int, column: int, escape: str) -> None:
        self.line = line
        self.column = column
        self.escape = escape

        super().__init__(line, column, escape)

    def __str__(self) -> str:
        return (
            "Expected numeric escape sequences to produce Unicode scalar values "
            "(U+0000 to U+D7FF or U+E000 to U+10FFFF) "
            f"at line {self.line}, column {self.column}. "
            f"Got '{self.escape}'."
        )
