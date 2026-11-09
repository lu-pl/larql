import lark


class LarqlError(lark.exceptions.LarkError):
    """Base exception for all larql errors.

    Subclassing lark.exceptions.LarkError allows calling code to catch
    either larql errors only or all Lark errors.
    """


class SPARQLSyntaxError(LarqlError):
    """Exception for indicating that a string does not conform to the SPARQL grammar.

    Note that this wraps the lark.exceptions.UnexpectedInput raised by the parser;
    the original exception is available as `__cause__`.
    """

    def __init__(self, line: int, column: int, context: str) -> None:
        self.line = line
        self.column = column
        self.context = context

        super().__init__(
            f"SPARQL syntax error at line {line}, column {column}:\n\n{context}"
        )


class SPARQLConstraintError(LarqlError):
    """Base exception for violations of constraints the grammar cannot express.

    Simple LarqlError subclass that allows calling code
    to address non-local exits from `ConstraintValidator`.
    """


class ValuesClauseError(SPARQLConstraintError):
    """Exception for indicating duplicate variables or row arity mismatches in VALUES clauses."""
