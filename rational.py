# Rational expressions

import numpy as np

from interval import Constraint
from nrta import Location, RTA, RTATran


class Expression:
    """Base class for rational expressions."""
    pass

class Epsilon(Expression):
    """Epsilon expression (recognizes the empty string)."""
    def __init__(self):
        pass

    def priority(self):
        return 100

    def __str__(self):
        return "eps"

    def __repr__(self):
        return "Epsilon()"

class Atom(Expression):
    """Atomic expression of the form (action, guard)."""
    def __init__(self, action, guard, index=None):
        assert isinstance(action, str) and isinstance(guard, Constraint)
        self.action = action
        self.guard = guard
        self.index = index

    def priority(self):
        return 100

    def __lt__(self, other):
        return (self.action, self.index) < (other.action, other.index)

    def __eq__(self, other):
        return self.action == other.action and self.guard == other.guard and self.index == other.index

    def __hash__(self):
        return hash(("ATOM", self.action, self.guard, self.index))

    def __str__(self):
        return "(%s,%s)" % (self.action, self.guard)

    def __repr__(self):
        if self.index is None:
            return "Atom(%s,%s)" % (repr(self.action), repr(self.guard))
        else:
            return "Atom(%s,%s,%s)" % (repr(self.action), repr(self.guard), self.index)

class Concat(Expression):
    """Concatenation of two rational expressions."""
    def __init__(self, expr1, expr2):
        assert isinstance(expr1, Expression) and isinstance(expr2, Expression)
        self.expr1 = expr1
        self.expr2 = expr2

    def priority(self):
        return 50

    def __str__(self):
        s1, s2 = str(self.expr1), str(self.expr2)
        if self.expr1.priority() < 50:
            s1 = "(" + s1 + ")"
        if self.expr2.priority() < 50:
            s2 = "(" + s2 + ")"
        return s1 + "." + s2

    def __repr__(self):
        return "Concat(%s,%s)" % (repr(self.expr1), repr(self.expr2))

class Union(Expression):
    """Union of two rational expressions."""
    def __init__(self, expr1, expr2):
        assert isinstance(expr1, Expression) and isinstance(expr2, Expression)
        self.expr1 = expr1
        self.expr2 = expr2

    def priority(self):
        return 20

    def __str__(self):
        s1, s2 = str(self.expr1), str(self.expr2)
        if self.expr1.priority() < 20:
            s1 = "(" + s1 + ")"
        if self.expr2.priority() < 20:
            s2 = "(" + s2 + ")"
        return s1 + "+" + s2

    def __repr__(self):
        return "Union(%s,%s)" % (repr(self.expr1), repr(self.expr2))

class Star(Expression):
    """Kleene star."""
    def __init__(self, expr):
        assert isinstance(expr, Expression)
        self.expr = expr

    def priority(self):
        return 100

    def __str__(self):
        if isinstance(self.expr, Atom):
            return "%s*" % self.expr
        else:
            return "(%s)*" % self.expr

    def __repr__(self):
        return "Star(%s)" % repr(self.expr)

def generateRandomAtom(actions, maxk):
    action = np.random.choice(actions, 1)[0]
    g1 = np.random.randint(0, maxk+2)
    if g1 == maxk+1:
        g2 = np.random.randint(0, maxk+1)
    else:
        g2 = np.random.randint(0, maxk+2)
    if g1 == g2:
        return Atom(action, Constraint("[%s,%s]" % (g1, g2)))
    if g1 > g2:
        g1, g2 = g2, g1

    # Case where the maximum is infinity
    if g2 == maxk+1:
        open1 = np.random.randint(0, 2)
        if open1 == 0:
            return Atom(action, Constraint("[%s,+)" % g1))
        else:
            return Atom(action, Constraint("(%s,+)" % g1))
    # Otherwise, both limits are finite
    else:
        open1 = np.random.randint(0, 2)
        open2 = np.random.randint(0, 2)
        if open1 == 0:
            if open2 == 0:
                return Atom(action, Constraint("[%s,%s]" % (g1, g2)))
            else:
                return Atom(action, Constraint("[%s,%s)" % (g1, g2)))
        else:
            if open2 == 0:
                return Atom(action, Constraint("(%s,%s]" % (g1, g2)))
            else:
                return Atom(action, Constraint("(%s,%s)" % (g1, g2)))

standard_constr = ['epsilon', 'atom', 'star', 'concat', 'union']
standard_prob = [0.02, 0.1, 0.13, 0.5, 0.25]

def build_star(expr):
    if isinstance(expr, Epsilon):
        return Epsilon()
    else:
        return Star(expr)

def build_concat(expr1, expr2):
    if isinstance(expr1, Epsilon):
        return expr2
    elif isinstance(expr2, Epsilon):
        return expr1
    else:
        return Concat(expr1, expr2)

def generateRandom(n_op, actions, maxk):
    if n_op == 0:
        return Epsilon()

    constr = np.random.choice(standard_constr, 1, p=standard_prob)
    if constr == 'epsilon':
        return Epsilon()
    elif constr == 'atom':
        return generateRandomAtom(actions, maxk)
    elif constr == 'star':
        return build_star(generateRandom(n_op-1, actions, maxk))
    elif constr == 'concat':
        return build_concat(generateRandom((n_op + 1) // 2, actions, maxk),
                            generateRandom(n_op // 2, actions, maxk))
    elif constr == 'union':
        if n_op == 1:
            return generateRandom(1, actions, maxk)
        else:
            return Union(generateRandom((n_op + 1) // 2, actions, maxk),
                         generateRandom(n_op // 2, actions, maxk))
    else:
        raise TypeError

def relabel(expr, start_index):
    """Relabel expr using the given starting index
    (numbering starts from start_index+1).
    
    """
    index = start_index

    def rec(e):
        nonlocal index
        if isinstance(e, Epsilon):
            return e
        elif isinstance(e, Atom):
            index += 1
            return Atom(e.action, e.guard, index=index)
        elif isinstance(e, Star):
            return Star(rec(e.expr))
        elif isinstance(e, Concat):
            return Concat(rec(e.expr1), rec(e.expr2))
        elif isinstance(e, Union):
            return Union(rec(e.expr1), rec(e.expr2))
        else:
            raise TypeError

    return rec(expr), index

def getLambda(expr):
    """Returns True if expr accepts the empty string, and False otherwise."""
    if isinstance(expr, Epsilon):
        return True
    elif isinstance(expr, Atom):
        return False
    elif isinstance(expr, Union):
        return getLambda(expr.expr1) or getLambda(expr.expr2)
    elif isinstance(expr, Concat):
        return getLambda(expr.expr1) and getLambda(expr.expr2)
    elif isinstance(expr, Star):
        return True
    else:
        raise TypeError

def getP(expr):
    """Set of initial atoms of an expression."""
    if isinstance(expr, Epsilon):
        return set()
    elif isinstance(expr, Atom):
        return set([expr])
    elif isinstance(expr, Union):
        return getP(expr.expr1).union(getP(expr.expr2))
    elif isinstance(expr, Concat):
        s1 = getP(expr.expr1)
        if getLambda(expr.expr1):
            return s1.union(getP(expr.expr2))
        else:
            return s1
    elif isinstance(expr, Star):
        return getP(expr.expr)
    else:
        raise TypeError

def getD(expr):
    """Set of final atoms of an expression."""
    if isinstance(expr, Epsilon):
        return set()
    elif isinstance(expr, Atom):
        return set([expr])
    elif isinstance(expr, Union):
        return getD(expr.expr1).union(getD(expr.expr2))
    elif isinstance(expr, Concat):
        s2 = getD(expr.expr2)
        if getLambda(expr.expr2):
            return s2.union(getD(expr.expr1))
        else:
            return s2
    elif isinstance(expr, Star):
        return getD(expr.expr)
    else:
        raise TypeError

def getF(expr):
    """Set of factors of length 2."""
    if isinstance(expr, (Epsilon, Atom)):
        return set()
    elif isinstance(expr, Union):
        return getF(expr.expr1).union(getF(expr.expr2))
    elif isinstance(expr, Concat):
        s1 = getF(expr.expr1).union(getF(expr.expr2))
        s2 = set()
        for d1 in getD(expr.expr1):
            for p2 in getP(expr.expr2):
                s2.add((d1, p2))
        return s1.union(s2)
    elif isinstance(expr, Star):
        s1 = getF(expr.expr)
        s2 = set()
        for d1 in getD(expr.expr):
            for p2 in getP(expr.expr):
                s2.add((d1, p2))
        return s1.union(s2)
    else:
        raise TypeError

def exprToRTA(expr, name, sigma, index):
    """Given a labeled expression, produce the corresponding RTA."""

    # Form the list of transitions
    trans = list()
    tran_id = 0

    # From initial state to P
    for p in sorted(list(getP(expr))):
        trans.append(RTATran(tran_id, source="1", label=p.action, constraint=p.guard, target=str(p.index)))
        tran_id += 1
    
    # One transition for each pair in F
    for f1, f2 in sorted(list(getF(expr))):
        trans.append(RTATran(tran_id, source=str(f1.index), label=f2.action,
                             constraint=f2.guard, target=str(f2.index)))
        tran_id += 1

    # Form the accepting states
    accepts = list()
    if getLambda(expr):
        accepts.append("1")
    for d in sorted(list(getD(expr))):
        accepts.append(str(d.index))
    accepts = sorted(accepts)

    # Form list of locations
    locations = list()
    for i in range(1, index+1):
        locations.append(Location(str(i), init=(i==1), accept=(str(i) in accepts)))

    rta = RTA(name, sigma, locations, trans, ["1"], accepts)
    return rta
