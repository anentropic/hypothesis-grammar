Hypothesis-Grammar
==================

[![Build Status](https://travis-ci.org/anentropic/hypothesis-grammar.svg?branch=master)](https://travis-ci.org/anentropic/hypothesis-grammar)
[![Latest PyPI version](https://badge.fury.io/py/hypothesis-grammar.svg)](https://pypi.python.org/pypi/hypothesis-grammar/)

![Python 3.7](https://img.shields.io/badge/Python%203.7--brightgreen.svg)
![Python 3.8](https://img.shields.io/badge/Python%203.8--brightgreen.svg)  

(pre-alpha... the stuff I've tried all works, not well tested yet though)

## What is it?

Hypothesis-Grammar is a "reverse parser" - given a grammar it will generate examples of that grammar.

It is implemented as a [Hypothesis](https://hypothesis.readthedocs.io/) strategy.

(If you are looking to generate text from a grammar for purposes other than testing with Hypothesis then this lib can still be useful, but I stongly recommend looking at the [tools provided with NLTK](http://www.nltk.org/howto/generate.html) instead.)

## Usage

So, how does this look?

First you need a grammar. Our grammar format is based on that used by the [Lark parser](https://lark-parser.readthedocs.io/en/latest/grammar/) library.  You can see our grammar-parsing grammar [here](hypothesis_grammar/grammar.lark). More details of our grammar format [below](#grammar-details).

Here is an example of using Hypothesis-Grammar:

```python
from hypothesis_grammar import strategy_from_grammar

st = strategy_from_grammar(
    grammar="""
        DET: "the" | "a"
        N: "man" | "park" | "dog"
        P: "in" | "with"

        s: np vp
        np: DET N
        pp: P np
        vp: "slept" | "saw" np | "walked" pp
    """,
    start="s",
)

st.example()
# ['a', 'dog', 'saw', 'the', 'man']

st.example()
# ['a', 'park', 'saw', 'a', 'man']

st.example()
# ['the', 'man', 'slept']
```

or as a test...

```python
from hypothesis import given
from hypothesis_grammar import strategy_from_grammar


@given(
    strategy_from_grammar(
        grammar="""
            DET: "the" | "a"
            N: "man" | "park" | "dog"
            P: "in" | "with"

            s: np vp
            np: DET N
            pp: P np
            vp: "slept" | "saw" np | "walked" pp
        """,
        start="s",
    )
)
def test_grammar(example):
    nouns = {"man", "park", "dog"}
    assert any(noun in example for noun in nouns)
```

The grammar is taken from an example in the NLTK docs and converted into our "simplified Lark" format.

`start="s"` tells the parser that the start rule is `s`.

As you can see, we have produced a Hypothesis strategy which is able to generate examples which match the grammar (in this case, short sentences which sometimes makes sense).

The output will always be a flat list of token strings. If you want a sentence you can just `" ".join(example)`.

But the grammar doesn't have to describe text, it might represent a sequence of actions for example. In that case you might want to convert your result tokens into object instances, which could be done via a lookup table.

(But if you're generating action sequences for tests then probably you should check out Hypothesis' [stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html) features first)

## Grammar details

- Whitespace is ignored
- 'Terminals' must be named all-caps (terminals only reference literals, not other rules), e.g. `DET`
- 'Rules' must be named all-lowercase, e.g. `np`
- LHS (name) and RHS are separated by `:` 
- String literals must be quoted with double-quotes e.g. `"man"`
- You can also use regex literals, they are delimited with forward-slash, e.g. `/the[a-z]{0,2}/`. Content for the regex token is generated using Hypothesis' [`from_regex`](https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.from_regex) strategy, with `fullmatch=True`.
- Adjacent tokens are concatenated, i.e. `DET N` means a `DET` followed by a `N`.
- `|` is alternation, so `"in" | "with"` means one-of `"in"` or `"with"`
- `?` means optional, i.e. `"in"?` means `"in"` is expected zero-or-one time.
- `*` i.e. `"in"*` means `"in"` is expected zero-or-many times.
- `+` i.e. `"in"+` means `"in"` is expected one-or-many times.
- `~ <num>` means exactly-&lt;num&gt; times.
- `~ <min>..<max>` is a range, expected between-&lt;min&gt;-and-&lt;max&gt; times.
- `(` and `)` are for grouping, the group can be quantified using any of the modifiers above.
