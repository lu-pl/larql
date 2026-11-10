import re
from collections.abc import Iterator
from typing import ClassVar

import lark

from larql.exceptions import CodepointEscapeError

_escape_pattern: re.Pattern[str] = re.compile(
    r"\\(?:u([0-9A-Fa-f]{4})|U([0-9A-Fa-f]{8})|.)"
)
r"""Pattern for scanning escape sequences in UCHAR terminals left-to-right.

The pattern captures two groups:
Group 1 captures the hex digits of a \uXXXX escape;
group 2 the hex digits of a \UXXXXXXXX escape;
for any other escape (e.g. \n or \\), both groups are None.

Note that the pattern also matches string escapes like \\ and \n, although only
numeric escapes are checked: read left-to-right, a backslash and the character
after it always form one escape, so in \\uD800 the second backslash belongs to
the string escape \\ and "uD800" is plain text. Since re.finditer resumes after
the end of each match, matching \\ as a whole keeps its second backslash from
starting a match of its own.

Also note that alternatives are tried in order and the first one that matches wins;
"." must come last, since it also matches u and U and would otherwise match
only the \u of \uD800.

The pattern doesn't validate escape syntax; the grammar already guarantees
well-formed escapes, e.g. exactly 4 hex digits after \u.
"""


class CodepointEscapeValidator(lark.Visitor):
    r"""Validator for numeric escape sequences that don't produce Unicode scalar values.

    See SPARQL 1.2 Query Language, 19.2 Escape Sequences:

        A numeric escape sequence MUST NOT produce a code point value
        in the range U+D800 to U+DFFF, which is the range for Unicode surrogates.

    The same section restricts \u escapes to U+0000 to U+D7FF and U+E000 to U+FFFF,
    and \U escapes to U+0000 to U+D7FF and U+E000 to U+10FFFF.

    Note that escape sequences are scanned left-to-right,
    so the code point of an escape is never part of another escape.
    """

    uchar_terminals: ClassVar[list[str]] = [
        "IRIREF",
        "STRING_LITERAL1",
        "STRING_LITERAL2",
        "STRING_LITERAL_LONG1",
        "STRING_LITERAL_LONG2",
    ]
    """Terminals whose productions allow [181] UCHAR numeric escapes.

    I.e. [159] IRIREF and the string literal terminals [176] to [179].
    """

    def __default__(self, tree: lark.Tree) -> None:
        for child in tree.children:
            match child:
                case lark.Token(type=token_type) if token_type in self.uchar_terminals:
                    _check_numeric_escapes(token=child)
                case _:  # not a terminal that allows numeric escapes
                    continue


def _check_numeric_escapes(token: lark.Token) -> None:
    for escape, codepoint in _get_numeric_escapes(value=token.value):
        if not _is_unicode_scalar_value(codepoint=codepoint):
            msg = (
                "Expected numeric escape sequences to produce Unicode scalar values "
                "(U+0000 to U+D7FF or U+E000 to U+10FFFF) "
                f"at line {token.line}, column {token.column}. "
                f"Got '{escape}'."
            )
            raise CodepointEscapeError(msg)


def _get_numeric_escapes(value: str) -> Iterator[tuple[str, int]]:
    for escape_match in _escape_pattern.finditer(value):
        match escape_match.groups():
            case (str(hex_digits), None) | (None, str(hex_digits)):
                yield escape_match.group(), int(hex_digits, 16)
            case (None, None):  # string escape, e.g. \n
                continue
            case _:  # pragma: no cover
                assert False, "This should never happen."


def _is_unicode_scalar_value(codepoint: int) -> bool:
    return 0x0 <= codepoint <= 0xD7FF or 0xE000 <= codepoint <= 0x10FFFF
