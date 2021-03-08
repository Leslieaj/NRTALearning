# Equivalence query using Hopcroft-Karp bisimulation up to congruence

import queue
import pprint

from interval import *
from nrta import Timedword, buildRTA, buildAssistantRTA
from fa import Timedlabel, alphabet_classify, rta_to_fa, fa_to_rta, nfa_to_dfa, alphabet_combine, alphabet_partitions, completed_dfa_complement, rfa_product

class Counterexample(object):
    def __init__(self, tws=None, value=-2):
        self.tws = tws
        self.value = value

    def __str__(self):
        return "%s, %s" % (self.tws, self.value)


class Pair:
    """A pair to process in the algorithm."""
    def __init__(self, X, Y, action, guard, pre):
        """X and Y are sets of locations.
        action is one of the actions in the automata.
        guard is an interval constraining the action.
        pre is the previous pair (None if initial pair).

        """
        self.X = X
        self.Y = Y
        self.action = action
        self.guard = guard
        self.pre = pre

    def __str__(self):
        return "%s ~ %s (%s, %s)" % (self.X, self.Y, self.action, self.guard)

    def __eq__(self, other):
        return self.X == other.X and self.Y == other.Y


def get_post(locs, action, guard, rta):
    """Get the set of locations reachable from locs using the given action
    and guard.

    """
    reachable = set()
    for loc in locs:
        for tran in rta.trans:
            if tran.source == loc and action == tran.label and guard.issubset(tran.constraint):
                reachable.add(tran.target)

    return reachable

def normalize(locs, R, *, side):
    """Normalize the set of locations considering the relations in R."""
    changed = True
    if side == 'hypothesis':
        locs = set('h' + loc for loc in locs)
    else:
        locs = set('t' + loc for loc in locs)
    pairs = []
    for pair in R:
        pairs.append((set('h' + loc for loc in pair.X), set('t' + loc for loc in pair.Y)))
    while changed:
        changed = False
        for X, Y in pairs:
            if X.issubset(locs) and not Y.issubset(locs):
                locs = locs.union(Y)
                changed = True
            elif Y.issubset(locs) and not X.issubset(locs):
                locs = locs.union(X)
                changed = True

    return locs

def can_accept(locs, rta):
    """Whether the set of locs contains an accepting location."""
    for loc in locs:
        if loc in rta.accept_names:
            return True
    return False

def build_ctx(pair, teacher):
    tws = []
    while pair.guard is not None:
        tws.append(Timedword(pair.action, min_constraint_number(pair.guard)))
        pair = pair.pre
    
    tws = list(reversed(tws))
    if teacher.is_accept(tws):
        return Counterexample(tws, 1)
    else:
        return Counterexample(tws, 0)

def equivalence_query(hypothesis, teacher, teacher_timed_alphabet):
    """hypothesis: the current nondeterministic real-time automaton hypothesis
    teacher: the real-time automaton hold by teacher
    """

    R = []
    todo = queue.Queue()
    all_pairs = []  # list of all pairs added

    todo.put(Pair(hypothesis.initstate_names, teacher.initstate_names, None, None, None))
    partitioned_alphabet, _ = alphabet_partitions(teacher_timed_alphabet)

    # print()
    while not todo.empty():
        cur_pair = todo.get()
        # print(cur_pair)

        # Check whether cur_pair is already in R or todo
        norm_X = normalize(cur_pair.X, R + list(todo.queue), side='hypothesis')
        norm_Y = normalize(cur_pair.Y, R + list(todo.queue), side='teacher')
        if norm_X == norm_Y:
            # print('cur_pair is redundant')
            continue

        # Check whether cur_pair gives a contradiction
        if can_accept(cur_pair.X, hypothesis) != can_accept(cur_pair.Y, teacher):
            ctx = build_ctx(cur_pair, teacher)
            # print('Found counterexample: %s' % ctx)
            return False, ctx

        for action in sorted(partitioned_alphabet.keys()):
            for timedlabel in partitioned_alphabet[action]:
                guard = timedlabel.constraints[0]
                next_X = get_post(cur_pair.X, action, guard, hypothesis)
                next_Y = get_post(cur_pair.Y, action, guard, teacher)

                next_pair = Pair(next_X, next_Y, action, guard, cur_pair)
                if next_pair not in all_pairs:
                    todo.put(next_pair)
                    all_pairs.append(next_pair)
        
        R.append(cur_pair)

    return True, Counterexample(None, -2)
