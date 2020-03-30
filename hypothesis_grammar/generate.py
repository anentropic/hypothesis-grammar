from typing import Iterator, List, Tuple

from hypothesis.core import given
from hypothesis._settings import HealthCheck, Phase, Verbosity, settings
from hypothesis.strategies import SearchStrategy

from hypothesis_grammar.types import intinf


def examples(strategy: SearchStrategy) -> List[Tuple[str, ...]]:
    """
    This is lifted from:
    hypothesis/strategies/_internal/strategies.py
    ...but adapted to remove restrictions on no of examples generated.

    DO NOT USE

    TODO:
    hypothesis generation is weird...

    When called, `example_generating_inner_function` will generate up to
    `max_examples` examples (non-unique, but the higher the limit the more
    variety you will see, and I believe `intinf` can exhaust the search
    space... it stops for simple examples at least)

    `example_generating_inner_function` does not return any value, so we have
    to 'post' data back into the containing func. I did not yet find a way to
    generate incrementally, although you can call `strategy.example()` in a
    loop (hypothesis uses `max_examples=10`) and get > 10 unique results, plus
    a lot of duplicates. So the max param biases the search space, but which
    examples are returned is random.
    """
    example_buffer = []

    @given(strategy)
    @settings(
        database=None,
        max_examples=intinf,
        deadline=None,
        verbosity=Verbosity.quiet,
        phases=(Phase.generate,),
        suppress_health_check=HealthCheck.all(),
    )
    def example_generating_inner_function(example):
        print("inner example:", example)
        example_buffer.append(tuple(example))

    example_generating_inner_function()
    return example_buffer
