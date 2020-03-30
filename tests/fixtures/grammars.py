NLTK_DEMO = """
DET: "the" | "a"
N: "man" | "park" | "dog"
P: "in" | "with"

s: np vp
np: DET N
pp: P np
vp: "slept" | "saw" np | "walked" pp
"""

A_BIT_OF_EVERYTHING = """
DET: "the" | "a"
N: "man" | "park" | "dog"
N2: "girl" | "restaurant" | "kitten"
P: "in" | "with"

s: (np vp) ~ 2..3
np: DET ( ( N | "woof" ~ 2 | "bow-wow" ) | N2 )
pp: P np
vp: "slept"+ | "saw" np | "walked"* pp?
"""

# Lark seems to implicitly concatenate the adjacent string literals
# `"with" "out"?` (while still respecting the ? quantifier) and will
# not recognise "with out", but our example results have each word as
# a discrete entry. This feels possibly like a bug in Lark's `%ignore WS`
# directive since everywhere else the tokens can be separated, but maybe
# it's deliberate 🤷‍♂️
FAILS_LARK_ROUNDTRIP = """
DET: "the" | "a"
N: "man" | "park" | "dog"
N2: "girl" | "restaurant" | "kitten"
P: "in" | "with" "out"?

s: (np vp) ~ 2..3
np: DET ( ( N | "woof" ~ 2 | "bow-wow" ) | N2 )
pp: P np
vp: "slept"+ | "saw" np | "walked"* pp
"""
