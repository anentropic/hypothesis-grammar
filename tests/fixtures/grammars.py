NLTK_DEMO = """
DET: "the" | "a"
N: "man" | "park" | "dog"
P: "in" | "with"

s: np vp
np: DET N
pp: P np
vp: "slept" | "saw" np | "walked" pp
"""

NLTK_DEMO2 = """
DET: "the" | "a"
N: "man" | "park" | "dog"
P: "in" | "with"

s: (np vp) ~ 2..4
np: DET N
pp: P np
vp: "slept" | "saw" np | "walked" pp
"""
