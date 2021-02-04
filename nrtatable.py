# observation table and membership query
import itertools, copy
from nrta import Timedword, Location
from regionautomaton import RATran, RegionAutomaton

class Element():
    """One row in table.
    """
    def __init__(self, rws=[], value=[], prime=False):
        self.rws = rws or []
        self.value = value or []
        self.prime = prime
    
    def __eq__(self, element):
        if self.rws == element.rws and self.value == element.value:
            return True
        else:
            return False

    def get_tws_e(self, e):
        rws_e = [tw for tw in self.rws]
        if len(e) == 0:
            return rws_e
        else:
            for rw in e:
                rws_e.append(rw)
            return rws_e

    def row(self):
        return self.value
    
    def whichstate(self):
        state_name = ""
        for v in self.value:
            state_name = state_name+str(v)
        return state_name
    
    def cover(self, r):
        """Whether self covers r. 
        "self covers r" means "r(v)==1 implies self(v)==1"
        """
        # if len(r.value) != len(self.value):
        #     return False
        result = True
        for v1, v2 in zip(r.value, self.value):
            if v1 == 1 and v2 != 1:
                result = False
                break
            else:
                pass
        return result
    
    def is_covered_by(self, r):
        """Whether self is covered by r.
        "self is covered by r" means "self(v)==1 implies r(v) == 1"
        """
        # if len(r.value) != len(self.value):
        #     return False
        result = True
        for v1, v2 in zip(r.value, self.value):
            if v2 == 1 and v1 != 1:
                result = False
                break
            else:
                pass
        return result

    def is_composed(self, primes):
        """Whether self is a composed row. primes is the collection of prime rows in S (the upper part of the table).
        If self is composed by some rows in primes, then self is a composed row.
        """
        if self in primes:
            return False
        length = len(primes)
        for i in range(1,length+1):
            i_combinations = list(itertools.combinations(primes, i))
            for tp in i_combinations:
                rows = [row for row in tp]
                join_value = rows_join(rows)
                if self.value == join_value:
                    return True
        return False

def rows_join(rows):
    """Given a rows list, join row.value. 0 join 0 = 0, 0 join 1 = 1, 1 join 0 = 1 , and 1 join 1 = 1.
    """
    if len(rows) == 1:
        return rows[0].value
    join_value = rows[0].value
    for i in range(1, len(rows)):
        tmp_value = [v1 or v2 for v1, v2 in zip(join_value, rows[i].value)]
        if len(tmp_value) != len(join_value):
            return [-1 for v in join_value]
        join_value = tmp_value
    return join_value

class Table(object):
    """Given a symbolic alphabet sigma = [a1, a2, ..., b1, b2, ...]
        R = S cdot sigma
    """
    def __init__(self, S = [], R = [], E = []):
        self.S = S
        self.R = R
        self.E = E
    
    def get_primes(self):
        """Return current prime rows
        """
        primes = [row for row in self.S if row.prime == True]
        return primes
    
    def update_primes(self):
        """Must be a closed table. Update the prime rows and composed rows (after we put a new element in S).
        """
        # check and update primes in S
        for s in self.S:
            temp_rows = [row for row in self.S if row != s]
            if s.is_composed(temp_rows) == False:
                s.prime = True
            else:
                s.prime = False
        # update primes in R
        # S_values = [s.value for s in self.S]
        primes = self.get_primes()
        prime_values = [p.value for p in primes]
        for r in self.R:
            if r.value in prime_values:
                r.prime = True
            else:
                r.prime = False
    
    def findrow_by_regionwords_in_R(self,regionword):
        for row in self.R:
            if regionword == row.rws:
                return row
    
    def findrow_by_regionwords_in_SR(self,regionword):
        allrows = [s for s in self.S] + [r for r in self.R]
        for row in allrows:
            if regionword == row.rws:
                return row
    
    def is_prepared(self, region_alphabet_list):
        flag_closed, move = self.is_closed()
        flag_consistent, new_a, new_e_index = self.is_consistent(region_alphabet_list)
        if flag_closed == True and flag_consistent == True:
            return True
        else:
            return False
    
    def is_closed(self):
        """Each row of R is composed of rows of prime rows in S.
        For each r in R, r = rows_join{s in primes(S) | s is covered by r}
        """
        prime_rows = self.get_primes()
        for r in self.R:
            temp_s = []
            for s in prime_rows:
                if s.is_covered_by(r) == True:
                    temp_s.append(s)
            if temp_s == []:
                return False, r
            join_value = rows_join(temp_s)
            if r.value != join_value:
                return False, r
        return True, None
    
    def is_consistent(self, region_alphabet_list):
        """Determine whether the table is consistent.
        For u, u' in S, a in sigma*, and u+a, u'+a in R, if u' is covered by u, then u'a is covered by ua.
        "region_alphabet_list": list version of the region_alphabet dict
        """
        flag = True
        new_a = None
        new_e_index = None
        if len(self.S) == 1:
            return True, new_a, new_e_index
        for i in range(0,len(self.S)): # u1
            for j in range(0,len(self.S)): # u2
                if i == j:
                    continue
                if self.S[j].is_covered_by(self.S[i]):
                    for regionlabel in region_alphabet_list:
                        u1_a = [rl for rl in self.S[i].rws] + [regionlabel]
                        u2_a = [rl for rl in self.S[j].rws] + [regionlabel]
                        row1 = self.findrow_by_regionwords_in_SR(u1_a)
                        row2 = self.findrow_by_regionwords_in_SR(u2_a)
                        if row2.is_covered_by(row1):
                            pass
                        else:
                            flag = False
                            new_a = regionlabel
                            for k in range(len(row1.value)):
                                if row2.value[k] == 1 and row1.value[k] == 0:
                                    new_e_index = k
                            return flag, new_a, new_e_index
        return flag, new_a, new_e_index
    
    def show(self):
        print("new_S:"+str(len(self.S)))
        for s in self.S:
            print([rl.show() for rl in s.rws], s.value, s.prime)
        print("new_R:"+str(len(self.R)))
        for r in self.R:
            print([rl.show() for rl in r.rws], r.value, r.prime)
        print("new_E:"+str(len(self.E)))
        for e in self.E:
            print([rl.show() for rl in e])

def make_closed(move, table, region_alphabet_list, rta):
    #flag, move = table.is_closed()
    new_E = table.E
    new_R = [r for r in table.R]
    new_R.remove(move)
    new_S = [s for s in table.S]
    new_S.append(move)
    closed_table = Table(new_S, new_R, new_E)

    closed_table.update_primes()
    prime_rows = table.get_primes()

    table_rws = [s.rws for s in closed_table.S] + [r.rws for r in closed_table.R]
    s_rws = [tw for tw in move.rws]
    for regionlabel in region_alphabet_list:
        temp_rws = s_rws+[regionlabel]
        if temp_rws not in table_rws:
            temp_element = Element(temp_rws,[])
            if temp_element.is_composed(prime_rows):
                temp_element.prime = False
            else:
                temp_element.prime = True
            fill(temp_element, closed_table.E, rta)
            closed_table.R.append(temp_element)
            table_rws = [s.rws for s in closed_table.S] + [r.rws for r in closed_table.R]
    return closed_table

def make_consistent(new_a, new_e_index, table, rta):
    #flag, new_a, new_e_index = table.is_consistent()
    #print flag
    new_E = [rws for rws in table.E]
    new_e = [new_a]
    if new_e_index > 0:
        e = table.E[new_e_index-1]
        new_e.extend(e)
    new_E.append(new_e)
    new_S = [s for s in table.S]
    new_R = [r for r in table.R]
    for i in range(0, len(new_S)):
        fill(new_S[i], new_E, rta)
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
    consistent_table = Table(new_S, new_R, new_E)
    consistent_table.update_primes()
    return consistent_table

def fill(element, E, rta):
    if len(element.value) == 0:
        f = rta.is_accept_rws(element.rws)
        element.value.append(f)
    #print len(element.value)-1, len(E)
    for i in range(len(element.value)-1, len(E)):
        temp_rws = element.rws + E[i]
        f = rta.is_accept_rws(temp_rws)
        element.value.append(f)

def suffixes(rws):
    """Return the suffixes of a regionwords. [rws1, rws2, rws3, ..., rwsn]
    """
    suffixes = []
    for i in range(0, len(rws)):
        temp_rws = rws[i:]
        suffixes.append(temp_rws)
    return suffixes

def add_ctx(nrtatable, region_alphabet, ctx, rta):
    """When receiving a counterexample ctx (a timedwords), first transiform it to a regionwords rws and then add the suffixes of rws to E
    (except those already present in E)
    """
    rws = []
    for tw in ctx:
        for rl in region_alphabet[tw.action]:
            if rl.region.isininterval(tw.time):
                rws.append(rl)
                break

    suff = suffixes(rws)
    new_S = [s for s in nrtatable.S]
    new_R = [r for r in nrtatable.R]
    new_E = [e for e in nrtatable.E] + [rws for rws in suff if rws not in nrtatable.E]
    for i in range(0, len(new_S)):
        fill(new_S[i], new_E, rta)
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
    return Table(new_S, new_R, new_E)

def table_to_ra(nrtatable, sigma, region_alphabet, n):
    """Given a prepared table, transform it to a region automaton.
    "n": the table index
    """
    region_alphabet_list = []
    for action in sigma:
        region_alphabet_list.extend(region_alphabet[action])
    locations = []
    initstate_names = []
    accept_names = []
    value_name_dict = {}
    # Locations
    table_elements = [s for s in nrtatable.S] + [r for r in nrtatable.R]
    epsilon_row = None
    for element in table_elements:
        if element.rws == []:
            epsilon_row = element
            break
    prime_rows = nrtatable.get_primes() # Q = primes(T)
    for s,i in zip(prime_rows, range(1, len(prime_rows)+1)):
        name = str(i)
        value_name_dict[s.whichstate()] = name
        init = False
        accept = False
        if s.is_covered_by(epsilon_row):
            init = True
            initstate_names.append(name)
        if s.value[0] == 1:
            accept = True
            accept_names.append(name)
        temp_state = Location(name, init, accept)
        locations.append(temp_state)
    # Transitions
    trans = []
    trans_number = len(trans)
    for u in nrtatable.S:
        if u.whichstate() in value_name_dict: # row(u) \in Q
            source = value_name_dict[u.whichstate()]
            for a in region_alphabet_list:
                temp = [rl for rl in u.rws] + [a]
                ua = nrtatable.findrow_by_regionwords_in_SR(temp)
                targets = []
                for r in prime_rows:
                    if r.is_covered_by(ua):
                        targets.append(value_name_dict[r.whichstate()])
                for target in targets:
                    need_newtran = True
                    for tran in trans:
                        if source == tran.source and target == tran.target and a.label == tran.label:
                            need_newtran = False
                            if a.index not in tran.alphabet_indexes:
                                tran.alphabet_indexes.append(a.index)
                            break
                    if need_newtran == True:
                        temp_tran = RATran(trans_number, source, target, a.label, [a.index])
                        trans.append(temp_tran)
                        trans_number = trans_number + 1
    for tran in trans:
        tran.alphabet_indexes.sort()
    RA = RegionAutomaton("RA"+str(n),region_alphabet,locations,trans,initstate_names,accept_names)
    return RA