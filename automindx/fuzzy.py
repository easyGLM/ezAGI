# fuzzy.py: A Comprehensive Guide to Fuzzy Logic Functions and Operations
# Author: Professor Codephreak
# License: MIT License, 2024

# Import necessary modules
from math import sqrt, exp, isinf, isnan, log
from typing import Any, Optional, Callable
from collections.abc import Callable
from functools import reduce
from numpy import multiply
import numpy as np
import matplotlib.pyplot as plt

# Functions that transform a given membership value to a truth value
def true(m):
    """The membership-value is its own truth-value."""
    return m

def false(m):
    """The opposite of TRUE."""
    return 1 - m

def fairly_false(m):
    """Part of a circle in quadrant I."""
    return sqrt(1 - m ** 2)

def fairly_true(m):
    """Part of a circle in quadrant II."""
    return sqrt(1 - (1 - m) ** 2)

def very_false(m):
    """Part of a circle in quadrant III."""
    return -sqrt(1 - (1 - m) ** 2)

def very_true(m):
    """Part of a circle in quadrant IV."""
    return -sqrt(1 - m ** 2)

# Functions to evaluate, infer, and defuzzify
def round_partial(value, res):
    """Round any value to any arbitrary precision."""
    return value if res == 0 or isinf(res) else round(value / res) * res

def rescale(out_min, out_max, *, in_min=0, in_max=1):
    """Scale from one domain to another."""
    assert in_min < in_max
    a = out_min
    b = out_max
    c = in_min
    d = in_max
    m = d - c
    n = a * d
    o = b * c
    def f(x):
        return (n - a * x - o + b * x) / m
    return f

def weighted_sum(*, weights: dict, target_d: 'Domain'):
    """Used for weighted decision trees and such."""
    assert sum(weights.values()) == 1
    rsc = rescale(target_d._low, target_d._high)
    def f(memberships):
        result = sum(r * weights[n] for n, r in memberships.items())
        return round_partial(rsc(result), target_d._res)
    return f

# Lingual hedges modify curves of membership values
def very(g):
    """Sharpen memberships so that only the values close to 1 stay at the top."""
    if isinstance(g, Set):
        def s_f(g):
            def f(x):
                return g(x) ** 2
            return f
        return Set(s_f(g.func), domain=g.domain, name=f"very_{g.name}")
    else:
        def f(x):
            return g(x) ** 2
        return f

def plus(g):
    """Sharpen memberships like 'very' but not as strongly."""
    if isinstance(g, Set):
        def s_f(g):
            def f(x):
                return g(x) ** 1.25
            return f
        return Set(s_f(g.func), domain=g.domain, name=f"plus_{g.name}")
    else:
        def f(x):
            return g(x) ** 1.25
        return f

def minus(g):
    """Increase membership support so that more values hit the top."""
    if isinstance(g, Set):
        def s_f(g):
            def f(x):
                return g(x) ** 0.75
            return f 
        return Set(s_f(g.func), domain=g.domain, name=f"minus_{g.name}")
    else:
        def f(x):
            return g(x) ** 0.75
        return f

# General-purpose functions that map R -> [0,1]
def inv(g: Callable[[float], float]) -> Callable:
    """Invert the given function within the unit-interval."""
    def f(x: float) -> float:
        return 1 - g(x)
    return f

def noop() -> Callable:
    """Do nothing and return the value as is."""
    def f(x: float) -> float:
        return x
    return f

def constant(c: float) -> Callable:
    """Return always the same value, no matter the input."""
    def f(_: Any) -> float:
        return c
    return f

def alpha(*, floor: float = 0, ceiling: float = 1, func: Callable, floor_clip: Optional[float] = None, ceiling_clip: Optional[float] = None):
    """Clip a function's values."""
    assert floor <= ceiling
    assert 0 <= floor
    assert ceiling <= 1
    floor_clip = floor if floor_clip is None else floor_clip
    ceiling_clip = ceiling if ceiling_clip is None else ceiling_clip
    def f(x: float) -> float:
        m = func(x)
        if m >= ceiling:
            return ceiling_clip
        elif m <= floor:
            return floor_clip
        else:
            return m
    return f

def normalize(height: float, func: Callable) -> Callable:
    """Map [0,1] to [0,1] so that max(array) == 1."""
    assert 0 < height <= 1
    def f(x: float) -> float:
        return func(x) / height
    return f

def moderate(func: Callable) -> Callable:
    """Map [0,1] -> [0,1] with bias towards 0.5."""
    def f(x: float) -> float:
        return 1 / 2 + 4 * (func(x) - 1 / 2) ** 3
    return f

# Membership Functions
def singleton(p: float, *, no_m: float = 0, c_m: float = 1):
    """A single spike."""
    assert 0 <= no_m < c_m <= 1
    def f(x: float) -> float:
        return c_m if x == p else no_m
    return f

def linear(m: float = 0, b: float = 0) -> Callable:
    """A textbook linear function with y-axis section and gradient."""
    def f(x: float) -> float:
        y = m * x + b
        if y <= 0:
            return 0
        elif y >= 1:
            return 1
        else:
            return y
    return f

def step(limit: float, /, *, left: float = 0, right: float = 1, at_lmt: Optional[float] = None) -> Callable:
    """A step function."""
    assert 0 <= left <= 1 and 0 <= right <= 1
    def f(x: float) -> float:
        if x < limit:
            return left
        elif x > limit:
            return right
        else:
            return at_lmt if at_lmt is not None else (left + right) / 2
    return f

def bounded_linear(low: float, high: float, *, c_m: float = 1, no_m: float = 0, inverse=False) -> Callable:
    """Variant of the linear function with gradient being determined by bounds."""
    assert low < high
    assert c_m > no_m
    if inverse:
        c_m, no_m = no_m, c_m
    gradient = (c_m - no_m) / (high - low)
    def g_0(_: Any) -> float:
        return (c_m + no_m) / 2
    if gradient == 0:
        return g_0
    def g_inf(x: float) -> float:
        asymptode = (high + low) / 2
        if x < asymptode:
            return no_m
        elif x > asymptode:
            return c_m
        else:
            return (c_m + no_m) / 2
    if isinf(gradient):
        return g_inf
    def f(x: float) -> float:
        y = gradient * (x - low) + no_m
        if y < 0:
            return 0.0
        return 1.0 if y > 1 else y
    return f

def R(low: float, high: float) -> Callable:
    """Simple alternative for bounded_linear()."""
    assert low < high
    def f(x: float) -> float:
        if x < low or isinf(high - low):
            return 0
        elif low <= x <= high:
            return (x - low) / (high - low)
        else:
            return 1
    return f

def S(low: float, high: float) -> Callable:
    """Simple alternative for bounded_linear."""
    assert low < high
    def f(x: float) -> float:
        if x <= low:
            return 1
        elif low < x < high:
            return high / (high - low) - x / (high - low)
        else:
            return 0
    return f

def rectangular(low: float, high: float, *, c_m: float = 1, no_m: float = 0) -> Callable:
    """Basic rectangular function that returns the core_y for the core else 0."""
    assert low < high
    def f(x: float) -> float:
        return no_m if x < low or high < x else c_m
    return f

def triangular(low: float, high: float, *, c: Optional[float] = None, c_m: float = 1, no_m: float = 0):
    """Basic triangular norm as combination of two linear functions."""
    assert low < high
    assert no_m < c_m
    c = c if c is not None else (low + high) / 2.0
    assert low < c < high
    left_slope = bounded_linear(low, c, no_m=0, c_m=c_m)
    right_slope = inv(bounded_linear(c, high, no_m=0, c_m=c_m))
    def f(x: float) -> float:
        return left_slope(x) if x <= c else right_slope(x)
    return f

def trapezoid(low: float, c_low: float, c_high: float, high: float, *, c_m: float = 1, no_m: float = 0):
    """Combination of rectangular and triangular, for convenience."""
    assert low < c_low <= c_high < high
    assert 0 <= no_m < c_m <= 1
    left_slope = bounded_linear(low, c_low, c_m=c_m, no_m=no_m)
    right_slope = bounded_linear(c_high, high, c_m=c_m, no_m=no_m, inverse=True)
    def f(x: float) -> float:
        if x < low or high < x:
            return no_m
        elif x < c_low:
            return left_slope(x)
        elif x > c_high:
            return right_slope(x)
        else:
            return c_m
    return f

def sigmoid(L: float, k: float, x0: float = 0):
    """Special logistic function."""
    assert 0 < L <= 1
    def f(x: float) -> float:
        if isnan(k * x):
            o = 1.0
        else:
            try:
                o = exp(-k * (x - x0))
            except OverflowError:
                o = float("inf")
        return L / (1 + o)
    return f

def bounded_sigmoid(low: float, high: float, inverse=False):
    """Calculate a weight based on the sigmoid function."""
    assert low < high
    if inverse:
        low, high = high, low
    k = (4.0 * log(3)) / (low - high)
    try:
        if isinf(k):
            p = 0.0
        elif isnan(-k * low):
            p = 1.0
        else:
            p = exp(-k * low)
    except OverflowError:
        p = float("inf")
    def f(x: float) -> float:
        try:
            q = 1.0 if (isinf(k) and x == 0) or (k == 0 and isinf(x)) else exp(x * k)
        except OverflowError:
            q = float("inf")
        r = p * q
        if isnan(r):
            r = 1
        return 1 / (1 + 9 * r)
    return f

def bounded_exponential(k: float = 0.1, limit: float = 1):
    """Function that goes through the origin and approaches a limit."""
    assert limit > 0
    assert k > 0
    def f(x: float) -> float:
        try:
            return limit - limit / exp(k * x)
        except OverflowError:
            return float(limit)
    return f

def simple_sigmoid(k: float = 0.229756):
    """Sigmoid variant with only one parameter (steepness)."""
    def f(x: float) -> float:
        if isinf(x) and k == 0:
            return 1 / 2
        try:
            return 1 / (1 + exp(x * -k))
        except OverflowError:
            return 0.0
    return f

def triangular_sigmoid(low: float, high: float, c: Optional[float] = None):
    """Version of triangular using sigmoids instead of linear."""
    assert low < high
    c = c if c is not None else (low + high) / 2.0
    assert low < c < high
    left_slope = bounded_sigmoid(low, c)
    right_slope = inv(bounded_sigmoid(c, high))
    def f(x: float) -> float:
        return left_slope(x) if x <= c else right_slope(x)
    return f

def gauss(c: float, b: float, *, c_m: float = 1) -> Callable:
    """Defined by ae^(-b(x-x0)^2), a gaussian distribution."""
    assert 0 < c_m <= 1
    assert 0 < b
    def f(x: float) -> float:
        try:
            o = (x - c) ** 2
        except OverflowError:
            return 0
        return c_m * exp(-b * o)
    return f

# Combinators for Fuzzy Sets
def MIN(*guncs) -> Callable:
    """Classic AND variant."""
    funcs = list(guncs)
    def F(z):
        return min(f(z) for f in funcs)
    return F

def MAX(*guncs):
    """Classic OR variant."""
    funcs = list(guncs)
    def F(z):
        return max((f(z) for f in funcs), default=1)
    return F

def product(*guncs):
    """AND variant."""
    funcs = list(guncs)
    def F(z):
        return reduce(multiply, (f(z) for f in funcs))
    return F

def bounded_sum(*guncs):
    """OR variant."""
    funcs = list(guncs)
    def op(x, y):
        return x + y - x * y
    def F(z):
        return reduce(op, (f(z) for f in funcs))
    return F

def lukasiewicz_AND(*guncs):
    """AND variant."""
    funcs = list(guncs)
    def op(x, y):
        return min(1, x + y)
    def F(z):
        return reduce(op, (f(z) for f in funcs))
    return F

def lukasiewicz_OR(*guncs):
    """OR variant."""
    funcs = list(guncs)
    def op(x, y):
        return max(0, x + y - 1)
    def F(z):
        return reduce(op, (f(z) for f in funcs))
    return F

def einstein_product(*guncs):
    """AND variant."""
    funcs = list(guncs)
    def op(x, y):
        return (x * y) / (2 - (x + y - x * y))
    def F(z):
        return reduce(op, (f(z) for f in funcs))
    return F

def einstein_sum(*guncs):
    """OR variant."""
    funcs = list(guncs)
    def op(x, y):
        return (x + y) / (1 + x * y)
    def F(z):
        return reduce(op, (f(z) for f in funcs))
    return F

def hamacher_product(*guncs):
    """AND variant."""
    funcs = list(guncs)
    def op(x, y):
        return (x * y) / (x + y - x * y) if x != 0 and y != 0 else 0
    def F(x):
        return reduce(op, (f(x) for f in funcs))
    return F

def hamacher_sum(*guncs):
    """OR variant."""
    funcs = list(guncs)
    def op(x, y):
        return (x + y - 2 * x * y) / (1 - x * y) if x != 1 or y != 1 else 1
    def F(z):
        return reduce(op, (f(z) for f in funcs))
    return F

def lambda_op(h):
    """A 'compensatoric' operator, combining AND with OR by a weighing factor l."""
    assert 0 <= h <= 1
    def E(*guncs):
        funcs = list(guncs)
        def op(x, y):
            return h * (x * y) + (1 - h) * (x + y - x * y)
        def F(z):
            return reduce(op, (f(z) for f in funcs))
        return F
    return E

def gamma_op(g):
    """Combine AND with OR by a weighing factor g."""
    assert 0 <= g <= 1
    def E(*guncs):
        funcs = list(guncs)
        def op(x, y):
            return (x * y) ** (1 - g) * ((1 - x) * (1 - y)) ** g
        def F(z):
            return reduce(op, (f(z) for f in funcs))
        return F
    return E

def simple_disjoint_sum(*funcs):
    """Simple fuzzy XOR operation."""
    def F(z):
        M = {f(z) for f in funcs}
        return max(min((x, *({1 - y for y in M - set([x])} or (1 - x,)))) for x in M)
    return F

# Domain, Set and Rule classes for fuzzy logic
class FuzzyWarning(UserWarning):
    """Extra Exception so that user code can filter exceptions specific to this lib."""
    pass

class Domain:
    """A domain is a 'measurable' dimension of 'real' values like temperature."""
    __slots__ = ["_name", "_low", "_high", "_res", "_sets"]
    def __init__(self, name: str, low: float, high: float, res: float = 1, sets: dict = None):
        assert low < high
        assert res > 0
        self._name = name
        self._high = high
        self._low = low
        self._res = res
        self._sets = {} if sets is None else sets  # Name: Set(Function())

    def __call__(self, x):
        """Pass a value to all sets of the domain and return a dict with results."""
        if not (self._low <= x <= self._high):
            raise FuzzyWarning(f"{x} is outside of domain!")
        return {name: s.func(x) for name, s in self._sets.items()}

    def __str__(self):
        """Return a string to print()."""
        return self._name

    def __repr__(self):
        """Return a string so that eval(repr(Domain)) == Domain."""
        return f"Domain('{self._name}', {self._low}, {self._high}, res={self._res}, sets={self._sets})"

    def __eq__(self, other):
        """Test equality of two domains."""
        return all([self._name == other._name, self._low == other._low, self._high == other._high, self._res == other._res, self._sets == other._sets])

    def __hash__(self):
        return id(self)

    def __getattr__(self, name):
        """Get the value of an attribute. Called after __getattribute__ is called with an AttributeError."""
        if name in self._sets:
            return self._sets[name]
        else:
            raise AttributeError(f"{name} is not a set or attribute")

    def __setattr__(self, name, value):
        """Define a set within a domain or assign a value to a domain attribute."""
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            assert str.isidentifier(name)
            if not isinstance(value, Set):
                value = Set(value)
            self._sets[name] = value
            value.domain = self
            value.name = name

    def __delattr__(self, name):
        """Delete a fuzzy set from the domain."""
        if name in self._sets:
            del self._sets[name]
        else:
            raise FuzzyWarning("Trying to delete a regular attr, this needs extra care.")

    @property
    def range(self):
        """Return an arange object with the domain's specifics."""
        if int(self._res) == self._res:
            return np.arange(self._low, self._high + self._res, int(self._res))
        else:
            return np.linspace(self._low, self._high, int((self._high - self._low) / self._res) + 1)

    def min(self, x):
        """Standard way to get the min over all membership funcs."""
        return min((f(x) for f in self._sets.values()), default=0)

    def max(self, x):
        """Standard way to get the max over all membership funcs."""
        return max((f(x) for f in self._sets.values()), default=0)

class Set:
    """A fuzzy set defines a 'region' within a domain."""
    name = None
    domain = None

    def __init__(self, func: Callable, *, name: str = None, domain: Domain = None):
        self.func = func
        self.domain = domain
        self.name = name
        self.__center_of_gravity = None

    def __call__(self, x):
        return self.func(x)

    def __invert__(self):
        """Return a new set with 1 - function."""
        return Set(inv(self.func), domain=self.domain)

    def __neg__(self):
        """Synonym for invert."""
        return Set(inv(self.func), domain=self.domain)

    def __and__(self, other):
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(MIN(self.func, other.func), domain=self.domain)

    def __or__(self, other):
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(MAX(self.func, other.func), domain=self.domain)

    def __mul__(self, other):
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(product(self.func, other.func), domain=self.domain)

    def __add__(self, other):
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(bounded_sum(self.func, other.func), domain=self.domain)

    def __xor__(self, other):
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(simple_disjoint_sum(self.func, other.func), domain=self.domain)

    def __pow__(self, power):
        """Return a new set with modified function."""
        return Set(lambda x: pow(self.func(x), power), domain=self.domain)

    def __eq__(self, other):
        """A set is equal with another if both return the same values over the same range."""
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Impossible to determine.")
        else:
            return np.array_equal(self.array(), other.array())

    def __le__(self, other):
        """If this <= other, it means this is a subset of the other."""
        assert self.domain == other.domain
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(np.less_equal(self.array(), other.array()))

    def __lt__(self, other):
        """If this < other, it means this is a proper subset of the other."""
        assert self.domain == other.domain
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(np.less(self.array(), other.array()))

    def __ge__(self, other):
        """If this >= other, it means this is a superset of the other."""
        assert self.domain == other.domain
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(np.greater_equal(self.array(), other.array()))

    def __gt__(self, other):
        """If this > other, it means this is a proper superset of the other."""
        assert self.domain == other.domain
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(np.greater(self.array(), other.array()))

    def __len__(self):
        """Number of membership values in the set, defined by bounds and resolution of domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        return len(self.array())

    @property
    def cardinality(self):
        """The sum of all values in the set."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        return sum(self.array())

    @property
    def relative_cardinality(self):
        """Relative cardinality is the sum of all membership values by number of all values."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        if len(self) == 0:
            raise FuzzyWarning("The domain has no element.")
        return self.cardinality / len(self)

    def concentrated(self):
        """Alternative to hedge 'very'."""
        return Set(lambda x: self.func(x) ** 2, domain=self.domain)

    def intensified(self):
        """Alternative to hedges."""
        def f(x):
            return 2 * self.func(x) ** 2 if x < 0.5 else 1 - 2 * (1 - self.func(x) ** 2)
        return Set(f, domain=self.domain)

    def dilated(self):
        """Expand the set with more values and already included values are enhanced."""
        return Set(lambda x: self.func(x) ** 1.0 / 2.0, domain=self.domain)

    def multiplied(self, n):
        """Multiply with a constant factor, changing all membership values."""
        return Set(lambda x: self.func(x) * n, domain=self.domain)

    def plot(self):
        """Graph the set in the given domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain assigned, cannot plot.")
        R = self.domain.range
        V = [self.func(x) for x in R]
        plt.plot(R, V)

    def array(self):
        """Return an array of all values for this set within the given domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain assigned.")
        return np.fromiter((self.func(x) for x in self.domain.range), float)

    def center_of_gravity(self):
        """Return the center of gravity for this distribution, within the given domain."""
        assert self.domain is not None
        weights = self.array()
        if sum(weights) == 0:
            return 0
        cog = np.average(self.domain.range, weights=weights)
        self.__center_of_gravity = cog
        return cog

    def __repr__(self):
        """Return a string representation of the Set that reconstructs the set with eval()."""
        return f"Set({self.func})"

    def __str__(self):
        """Return a string for print()."""
        if self.domain is not None:
            return f"{self.domain._name}.{self.name}"
        if self.name is None:
            return f"dangling Set({self.func})"
        else:
            return f"dangling Set({self.name}"

    def normalized(self):
        """Return a set that is normalized *for this domain* with 1 as max."""
        if self.domain is None:
            raise FuzzyWarning("Can't normalize without domain.")
        return Set(normalize(max(self.array()), self.func), domain=self.domain)

    def __hash__(self):
        return id(self)

class Rule:
    """A collection of bound sets that span a multi-dimensional space of their respective domains."""
    def __init__(self, conditions, func=None):
        self.conditions = {frozenset(C): oth for C, oth in conditions.items()}
        self.func = func

    def __add__(self, other):
        assert isinstance(other, Rule)
        return Rule({**self.conditions, **other.conditions})

    def __radd__(self, other):
        assert isinstance(other, (Rule, int))
        if isinstance(other, int):
            return self
        return Rule({**self.conditions, **other.conditions})

    def __or__(self, other):
        assert isinstance(other, Rule)
        return Rule({**self.conditions, **other.conditions})

    def __eq__(self, other):
        return self.conditions == other.conditions

    def __getitem__(self, key):
        return self.conditions[frozenset(key)]

    def __call__(self, args: dict[Domain, float], method="cog"):
        """Calculate the inferred value based on different methods. Default is center of gravity (cog)."""
        assert len(args) == max(len(c) for c in self.conditions.keys())
        assert isinstance(args, dict)
        if method == "cog":
            assert len({C.domain for C in self.conditions.values()}) == 1
            actual_values = {f: f(args[f.domain]) for S in self.conditions.keys() for f in S}
            weights = []
            for K, v in self.conditions.items():
                x = min((actual_values[k] for k in K if k in actual_values), default=0)
                if x > 0:
                    weights.append((v, x))
            if not weights:
                return None
            target_domain = list(self.conditions.values())[0].domain
            index = sum(v.center_of_gravity * x for v, x in weights) / sum(x for v, x in weights)
            return (target_domain._high - target_domain._low) / len(target_domain.range) * index + target_domain._low
        else:
            raise ValueError("Invalid method.")

def rule_from_table(table: str, references: dict):
    """Turn a (2D) string table into a Rule of fuzzy sets."""
    import io
    from itertools import product
    import pandas as pd
    df = pd.read_table(io.StringIO(table), sep=r"\s+")
    D = {
        (eval(df.index[x].strip(), references), eval(df.columns[y].strip(), references)): eval(df.iloc[x, y], references)
        for x, y in product(range(len(df.index)), range(len(df.columns)))
    }
    return Rule(D)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
