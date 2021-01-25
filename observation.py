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

class Table():
    """observation table.
    """
    def __init__(self, S = None, R = None, E=[]):
        self.S = S
        self.R = R
        self.E = E  #if E is empty, it means that there is an empty action in E.
    
    def is_closed(self):
        """Each row of R is composed of rows of S.
        For each r in R, r = rows_join{s in S | s is covered by r}
        """
        for r in self.R:
            temp_s = []
            for s in self.S:
                if s.is_covered_by(r) == True:
                    temp_s.append(s)
            join_value = rows_join(temp_s)
            if r.value != join_value:
                return False, r
        return True, None
    
    def is_consistent(self):
        """Determine whether the table is consistent.
        For u, u' in S U R, a in sigma*, and u+a, u'+a in S U R, if u' is covered by u, then u'a is covered by ua.
        """
        flag = True
        new_a = None
        new_e_index = None
        table_element = [s for s in self.S] + [r for r in self.R]
        for i in range(0, len(table_element)):   # u
            for j in range(0, len(table_element)): # u'
                if table_element[j] == table_element[i]:
                    continue
                if table_element[j].is_covered_by(table_element[i]):
                    temp_elements1 = []
                    temp_elements2 = []
                    #print len(table_element[2].tws), [tw.show() for tw in table_element[2].tws]
                    for element in table_element:
                        #print "element", [tw.show() for tw in element.tws]
                        if is_prefix(element.tws, table_element[i].tws):
                            new_element1 = Element(delete_prefix(element.tws, table_element[i].tws), [v for v in element.value])
                            temp_elements1.append(new_element1)
                        if is_prefix(element.tws, table_element[j].tws):
                            #print "e2", [tw.show() for tw in element.tws]
                            new_element2 = Element(delete_prefix(element.tws, table_element[j].tws), [v for v in element.value])
                            temp_elements2.append(new_element2)
                    for e1 in temp_elements1:
                        for e2 in temp_elements2:
                            #print [tw.show() for tw in e1.tws], [tw.show() for tw in e2.tws]
                            if len(e1.tws) == 1 and len(e2.tws) == 1 and e1.tws == e2.tws:
                                if e2.is_covered_by(e1):
                                    pass
                                else:
                                    flag = False
                                    new_a = e1.tws
                                    for i in range(0, len(e1.value)):
                                        if e2.value[i] == 1 and e1.value[i] == 0:
                                            new_e_index = i
                                            return flag, new_a, new_e_index
        return flag, new_a, new_e_index

    def is_evidence_closed(self):
        """Determine whether the table is evidence-closed.
        """
        flag = True
        table_tws = [s.tws for s in self.S] + [r.tws for r in self.R]
        #new_R = [r for r in self.R]
        new_added = []
        for s in self.S:
            for e in self.E:
                temp_se = [tw for tw in s.tws] + [tw for tw in e]
                if temp_se not in table_tws:
                    table_tws.append(temp_se)
                    new_tws = temp_se
                    new_element = Element(new_tws,[])
                    #new_R.append(new_element)
                    new_added.append(new_element)
        if len(new_added) > 0:
            flag = False
        return flag, new_added
    
    def show(self):
        print("new_S:"+str(len(self.S)))
        for s in self.S:
            print([tw.show() for tw in s.tws], s.value)
        print("new_R:"+str(len(self.R)))
        for r in self.R:
            print([tw.show() for tw in r.tws], r.value)
        print("new_E:"+str(len(self.E)))
        for e in self.E:
            print([tw.show() for tw in e])
    
def make_closed(move, table, sigma, rta):
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

def make_consistent(new_a, new_e_index, table, sigma, rta):
    #flag, new_a, new_e_index = table.is_consistent()
    #print flag
    new_E = [tws for tws in table.E]
    new_e = [tw for tw in new_a]
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
    return consistent_table

def make_evidence_closed(new_added, table, sigma, rta):
    #flag, new_added = table.is_evidence_closed()
    for i in range(0,len(new_added)):
        fill(new_added[i], table.E, rta)
    new_E = [e for e in table.E]
    new_R = [r for r in table.R] + [nr for nr in new_added]
    new_S = [s for s in table.S]
    evidence_closed_table = Table(new_S, new_R, new_E)
    return evidence_closed_table




def prefixes(tws):
    """Return the prefixes of a timedwords. [tws1, tws2, tws3, ..., twsn]
    """
    prefixes = []
    for i in range(1, len(tws)+1):
        temp_tws = tws[:i]
        prefixes.append(temp_tws)
    return prefixes

def is_prefix(tws, pref):
    """Determine whether the pref is a prefix of the timedwords tws
    """
    if len(pref) == 0:
        return True
    else:
        if len(tws) < len(pref):
            return False
        else:
            for i in range(0, len(pref)):
                if tws[i] == pref[i]:
                    pass
                else:
                    return False
            return True

def delete_prefix(tws, pref):
    """Delete a prefix of timedwords tws, and return the new tws
    """
    if len(pref) == 0:
        return [tw for tw in tws]
    else:
        new_tws = tws[len(pref):]
        return new_tws

def fill(element, E, rta):
    if len(element.value) == 0:
        f = rta.is_accept(element.tws)
        element.value.append(f)
    #print len(element.value)-1, len(E)
    for i in range(len(element.value)-1, len(E)):
        temp_tws = element.tws + E[i]
        f = rta.is_accept(temp_tws)
        element.value.append(f)

def add_ctx(table, ctx, rta):
    """When receiving a counterexample ctx (a timedwords), add it and its prefixes to R
    (except those already present in S U R)
    """
    pref = prefixes(ctx)
    S_R_tws = [s.tws for s in table.S] + [r.tws for r in table.R]
    new_S = [s for s in table.S]
    new_R = [r for r in table.R]
    new_E = [e for e in table.E]
    for tws in pref:
        need_add = True
        for stws in S_R_tws:
            if tws == stws:
                need_add = False
        if need_add == True:
            temp_element = Element(tws,[])
            fill(temp_element, new_E, rta)
            new_R.append(temp_element)
    return Table(new_S, new_R, new_E)
