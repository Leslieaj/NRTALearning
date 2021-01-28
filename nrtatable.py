# observation table and membership query
import itertools
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

    def is_composed(self, S):
        """Whether self is a composed row. S is the upper part of the table and we keep all elements in S be prime rows.
        If self is composed by some rows in S, then self is a composed row.
        """
        # if self in S:
        #     return True
        length = len(S)
        for i in range(1,length+1):
            i_combinations = list(itertools.combinations(S, i))
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
    """Given a symbolic alphabet  sigma = [a1, a2, ..., b1, b2, ...]
        R = S cdot sigma
    """
    def __init__(self, S = [], R = [], E = []):
        self.S = S
        self.R = R
        self.E = E
    
    
    
