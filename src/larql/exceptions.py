import lark


class SemanticConstraintError(lark.exceptions.LarkError):
    """Base exception for semantic constraint violations.

    Simple lark.exceptions.LarkError subclass that allows calling code
    to address non-local exits from `SemanticConstraintValidator`.
    """


class ValuesClauseError(SemanticConstraintError):
    """Exception for indicating duplicate variables or row arity mismatches in VALUES clauses."""
