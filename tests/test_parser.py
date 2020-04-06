from hypothesis import given
from lark import Lark, Tree

from hypothesis_grammar import strategy_from_grammar

from tests.fixtures.grammars import A_BIT_OF_EVERYTHING, FAILS_LARK_ROUNDTRIP


def larkify(grammar: str) -> str:
    return f"""
%import common.WS
%ignore WS

{grammar}
"""


@given(
    strategy_from_grammar(
        grammar=A_BIT_OF_EVERYTHING,
        start="s",
    )
)
def test_roundtrip(example):
    """
    Since our grammar-parsing grammar is derived from a subset of
    Lark's grammar, any user-grammar should be usable as a Lark grammer.
    So we should be able to parse the generated example using a parser
    from the user-grammar, giving us a hacky round-trip property.

    See `FAILS_LARK_ROUNDTRIP` test grammar for an example that fails
    (our output doesn't seem wrong, but there is an inconsistency
    with Lark parser behaviour....)
    """
    roundtrip_parser = Lark(
        larkify(A_BIT_OF_EVERYTHING),
        start="s",
    )
    stringified = " ".join(example)
    result = roundtrip_parser.parse(stringified)
    assert isinstance(result, Tree)


@given(
    strategy_from_grammar(
        grammar=FAILS_LARK_ROUNDTRIP,
        start="s",
    )
)
def test_roundtrip_no_larkify(example):
    """
    This fails if we use `larkify` and `" ".join(...)` due to an
    inconsistency in how Lark `%ignore WS` directive is interpreted.
    But since our grammar has no explicit handling of whitespace, if
    we round-trip without that directive and without inserting space
    between tokens, then it should pass.
    """
    roundtrip_parser = Lark(FAILS_LARK_ROUNDTRIP, start="s")
    stringified = "".join(example)
    result = roundtrip_parser.parse(stringified)
    assert isinstance(result, Tree)
