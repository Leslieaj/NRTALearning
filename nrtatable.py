# observation table and membership query
import itertools, copy
from nrta import Timedword

class Element():
    """One row in table.
    """
    def __init__(self, tws=[], value=[], prime=False):
        self.tws = tws or []
        self.value = value or []
        self.prime = False
    
    def __eq__(self, element):
        if self.tws == element.tws and self.value == element.value:
            return True
        else:
            return False

    def get_tws_e(self, e):
        tws_e = [tw for tw in self.tws]
        if len(e) == 0:
            return tws_e
        else:
            for tw in e:
                tws_e.append(tw)
            return tws_e

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
            if regionword == row.tws:
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
        for i in range(0,len(self.S)): # u1
            for j in range(1,len(self.S)+1): # u2
                if self.S[j].is_covered_by(self.S[i]):
                    for regionlabel in region_alphabet_list:
                        u1 = copy.deepcopy(self.S[i])
                        u2 = copy.deepcopy(self.S[j])
                        u1_a = u1.append(regionlabel)
                        u2_a = u2.append(regionlabel)
                        row1 = self.findrow_by_regionwords_in_R(u1_a)
                        row2 = self.findrow_by_regionwords_in_R(u2_a)
                        if row2.is_covered_by(row1):
                            pass
                        else:
                            flag = False
                            new_a = regionlabel
                            for k in range(len(row1)):
                                if row2.value[k] == 1 and row1.value[k] == 0:
                                    new_e_index = k
                            return flag, new_a, new_e_index
        return flag, new_a, new_e_index

def make_closed(move, table, region_alphabet_list, rta):
    #flag, move = table.is_closed()
    new_E = table.E
    new_R = [r for r in table.R]
    new_R.remove(move)
    new_S = [s for s in table.S]
    new_S.append(move)
    closed_table = Table(new_S, new_R, new_E)
    table_tws = [s.tws for s in closed_table.S] + [r.tws for r in closed_table.R]
    
    s_tws = [tw for tw in move.tws]
    for action in sigma:
        temp_tws = s_tws+[Timedword(action,0)]
        if temp_tws not in table_tws:
            temp_element = Element(temp_tws,[])
            fill(temp_element, closed_table.E, rta)
            closed_table.R.append(temp_element)
            table_tws = [s.tws for s in closed_table.S] + [r.tws for r in closed_table.R]
    return closed_table