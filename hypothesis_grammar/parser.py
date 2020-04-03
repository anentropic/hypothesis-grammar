from ast import literal_eval
from itertools import chain
from pathlib import Path
from typing import Iterable, List, TypeVar, Union

import inject
from hypothesis import strategies as st
from lark import Lark, Token, Transformer

from hypothesis_grammar.types import Deps, Modifiers


def _configure(binder):
    path = Path(__file__).parent / Path("grammar.lark")

    def load_parser() -> Lark:
        # load the grammar-parsing grammar into a parser
        with open(path) as f:
            return Lark(f)

    binder.bind(Deps.GRAMMAR_PATH, path)
    binder.bind_to_constructor(Deps.GRAMMAR_PARSER, load_parser)


inject.configure(_configure)


def _concat(children: Iterable[st.SearchStrategy]) -> st.SearchStrategy:
    @st.composite
    def concat_(draw):
        return list(chain.from_iterable(
            draw(from_strategy) for from_strategy in children
        ))

    constituents = " + ".join(repr(st) for st in children)
    strategy = concat_()
    strategy.function.__name__ = f"concat<{constituents}>"
    return strategy


def _chain(lists: st.SearchStrategy) -> st.SearchStrategy:
    @st.composite
    def chain_(draw):
        return list(chain.from_iterable(draw(lists)))

    strategy = chain_()
    strategy.function.__name__ = f"chained<{repr(lists)}>"
    return strategy


def _listify(single: st.SearchStrategy) -> st.SearchStrategy:
    """
    Put the result of `single` strategy into a list
    (all strategies should return lists)
    """
    @st.composite
    def listify_(draw):
        return [draw(single)]

    strategy = listify_()
    strategy.function.__name__ = f"listified<{repr(single)}>"
    return strategy


T = TypeVar("T", bound=st.SearchStrategy)


class StrategyBuilder(Transformer):
    def __init__(self, start: str):
        self.strategies = {}
        self._start = start

    def STRING(self, token: Token) -> st.SearchStrategy:
        # (all strategies should return lists)
        return st.just([literal_eval(token.value)])

    def REGEXP(self, token: Token) -> st.SearchStrategy:
        # regex is /delimited/
        return _listify(st.from_regex(token.value[1:-1], fullmatch=True))

    def _flatten(self, children: List[T]) -> T:
        return children[0]

    def _store_st(self, top_level: List[Union[Token, T]]) -> T:
        token, strategy = top_level
        self.strategies[token.value] = strategy
        return strategy

    def _deferred(self, name: str) -> st.SearchStrategy:
        def strategy_for_token():
            return self.strategies[name]

        strategy_for_token.__name__ = f"strategy_for_token[{name}]"
        return st.deferred(strategy_for_token)

    def terminal(self, children: List[Token]) -> st.SearchStrategy:
        return self.strategies[children[0].value]

    def nonterminal(self, children: List[Token]) -> st.SearchStrategy:
        return self._deferred(children[0].value)

    def expansions(
        self, children: Union[st.SearchStrategy, List[st.SearchStrategy]]
    ) -> st.SearchStrategy:
        # (alternation)
        if isinstance(children, st.SearchStrategy):
            return children
        elif len(children) == 1:
            return children[0]
        else:
            assert isinstance(children[0], st.SearchStrategy)
            assert isinstance(children[1], st.SearchStrategy)
            return st.one_of(children[0], children[1])

    def concatenation(
        self, children: Union[st.SearchStrategy, List[st.SearchStrategy]]
    ) -> st.SearchStrategy:
        if isinstance(children, st.SearchStrategy):
            return children
        elif len(children) == 1:
            return children[0]
        else:
            for child in children:
                assert isinstance(child, st.SearchStrategy)
            return _concat(children)

    def expr(
        self, children: List[Union[st.SearchStrategy, Token]]
    ) -> st.SearchStrategy:
        strategy, modifier, *params = children
        modifier = Modifiers(modifier.value)
        params = [int(p.value) for p in params]

        if modifier is Modifiers.QUANTIFIED:
            assert params
            if len(params) == 1:
                min_ = max_ = params[0]
            elif len(params) == 2:
                min_, max_ = params
            else:
                raise TypeError(params)
        elif modifier is Modifiers.ONE_OR_MORE:
            min_ = 1
            max_ = None
        elif modifier is Modifiers.ZERO_OR_MORE:
            min_ = 0
            max_ = None
        elif modifier is Modifiers.OPTIONAL:
            min_ = 0
            max_ = 1

        assert isinstance(strategy, st.SearchStrategy)
        return _chain(st.lists(strategy, min_size=min_, max_size=max_))

    def start(self, _) -> st.SearchStrategy:
        # 'start' token is the root node of the tree, return result
        return self.strategies[self._start]

    literal = value = _flatten

    rule = term = _store_st


@inject.params(parser=Deps.GRAMMAR_PARSER)
def strategy_from_grammar(grammar: str, start: str, parser: Lark) -> st.SearchStrategy:
    tree = parser.parse(grammar)
    # print(tree.pretty())
    strategy = StrategyBuilder(start).transform(tree)
    return strategy
