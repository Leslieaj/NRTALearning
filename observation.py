# observation table and membership query
#import itertools
import math
from nrta import Timedword

class Element():
    """One row in table.
    """
    def __init__(self, tws=[], value=[], prime=False):
        self.tws = tws or []
        self.value = value or []
        self.prime = False
        self.sv = self.whichstate()
    
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
        # return "".join(str(v) for v in self.value)
    
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
        rows = []
        for s in S:
            if s.is_covered_by(self):
                rows.append(s)
        if len(rows) == 0:
            return False
        join_value = rows_join(rows)
        if self.value == join_value:
            return True
        else:
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
    
    def is_prepared(self):
        flag_closed, move = self.is_closed()
        flag_consistent, new_a, new_e_index = self.is_consistent()
        flag_distinct, new_elements = self.is_source_distinct()
        # flag_evid_closed, new_added = self.is_evidence_closed()
        # if flag_closed == True and flag_consistent == True and flag_distinct == True and flag_evid_closed == True:
        if flag_closed == True and flag_consistent == True and flag_distinct == True:
        # if flag_closed == True and flag_distinct == True:
            print("Table is prepared.")
            return True
        else:
            print("Not prepared.")
            return False
    
    def is_closed(self):
        """Each row of R is composed of rows of S.
        For each r in R, r = rows_join{s in S | s is covered by r}
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
    
    def is_consistent(self):
        """Determine whether the table is consistent.
        For u, u' in S U R, a in sigma*, and u+a, u'+a in S U R, if u' is covered by u, then u'a is covered by ua.
        """
        flag = True
        new_a = None
        new_e_index = None
        table_element = [s for s in self.S] + [r for r in self.R]
        table_mapping = dict()
        for element in table_element:
            table_mapping[tuple(element.tws)] = element
        for i in range(0, len(table_element)):   # ua
            for j in range(0, len(table_element)): # u'a
                if table_element[j].tws == table_element[i].tws or table_element[j].tws == [] or table_element[i].tws == []:
                    continue
                if table_element[j].tws[-1] == table_element[i].tws[-1] and not table_element[j].is_covered_by(table_element[i]):
                    u1 = table_element[i].tws[:-1]
                    u2 = table_element[j].tws[:-1]
                    temp_element1 = table_mapping[tuple(u1)]
                    temp_element2 = table_mapping[tuple(u2)]
                    if temp_element2.is_covered_by(temp_element1):
                        for k in range(0, len(table_element[i].value)):
                            if table_element[j].value[k] == 1 and table_element[i].value[k] == 0:
                                new_a = [table_element[i].tws[-1]]
                                new_e_index = k
                                flag = False
                                return flag, new_a, new_e_index
        return flag, new_a, new_e_index

    def is_evidence_closed(self):
        """Determine whether the table is evidence-closed.
        """
        flag = True
        table_tws = [s.tws for s in self.S] + [r.tws for r in self.R]
        #new_R = [r for r in self.R]
        new_added = []
        prime_rows = self.get_primes()
        for s in prime_rows:
            for e in self.E:
                pre_e_list = prefixes(e)
                for pre_e in pre_e_list:
                    temp_se = [tw for tw in s.tws] + [tw for tw in pre_e]
                    if temp_se not in table_tws:
                        table_tws.append(temp_se)
                        new_tws = temp_se
                        new_element = Element(new_tws,[])
                    #new_R.append(new_element)
                        new_added.append(new_element)
        if len(new_added) > 0:
            flag = False
        return flag, new_added
    
    def is_source_distinct(self):
        """ For u in S_R, if u is composed by prime rows s1, s2, ... sn and u+a is in S_R,  si+a should in S_R
        """
        flag = True
        table_elements = [s for s in self.S] + [r for r in self.R]
        table_tws = [s.tws for s in self.S] + [r.tws for r in self.R]
        self.update_primes()
        prime_rows = self.get_primes()
        new_elements = []
        table_mapping = dict()
        for element in table_elements:
            table_mapping[tuple(element.tws)] = element
        for ua in table_elements:
            if ua.tws == []:
                continue
            u = table_mapping[tuple(ua.tws[:-1])]
            a = ua.tws[-1]
            tws_sources = [p.tws for p in prime_rows if p.is_covered_by(u)]
            new_tws_list = []
            for p_tws in tws_sources:
                new_tws = p_tws + [a]
                if new_tws not in new_tws_list and (new_tws not in table_tws):
                    flag = False
                    new_tws_list.append(new_tws)
                    new_elements.append(Element(new_tws,[]))
        return flag, new_elements

    def show(self):
        print("new_S:"+str(len(self.S)))
        index = 1
        for s in self.S:
            print(index, [tw.show() for tw in s.tws], s.value, s.prime)
            index = index + 1
        print("new_R:"+str(len(self.R)))
        for r in self.R:
            print(index, [tw.show() for tw in r.tws], r.value, r.prime)
            index = index + 1
        print("new_E:"+str(len(self.E)))
        for e in self.E:
            print([tw.show() for tw in e])

def make_prepared(table, t_number, sigma, rta):
    t = table
    flag_closed, move = t.is_closed()
    if flag_closed == False:
        print("Not closed")
        temp = make_closed(move, t, sigma, rta)
        t = temp
        t_number = t_number + 1
        print("Table " + str(t_number))
        print("S+R:", len(t.S)+len(t.R), "E:", len(t.E)+1)
        # t.show()
        print("--------------------------------------------------")
    flag_distinct, new_elements = t.is_source_distinct()
    if flag_distinct == False:
        print("Not source distinct")
        temp = make_source_distinct(new_elements, t, rta)
        t = temp
        t_number = t_number + 1
        print("Table " + str(t_number))
        print("S+R:", len(t.S)+len(t.R), "E:", len(t.E)+1)
        # t.show()
        print("--------------------------------------------------")
    flag_consistent, new_a, new_e_index = t.is_consistent()
    if flag_consistent == False:
        print("Not consistent")
        temp = make_consistent(new_a, new_e_index, t, sigma, rta)
        t = temp
        t_number = t_number + 1
        print("Table " + str(t_number))
        print("S+R:", len(t.S)+len(t.R), "E:", len(t.E)+1)
        # t.show()
        print("--------------------------------------------------")
    # flag_evid_closed, new_added = t.is_evidence_closed()
    # if flag_evid_closed == False:
    #     print("Not evidence closed")
    #     temp = make_evidence_closed(new_added, t, sigma, rta)
    #     t = temp
    #     t_number = t_number + 1
    #     print("Table " + str(t_number))
    #     print("S+R:", len(t.S)+len(t.R), "E:", len(t.E)+1)
    #     # t.show()
    #     print("--------------------------------------------------")
    # if flag_closed == True and flag_distinct == True and flag_consistent == True and flag_evid_closed == True:
    if flag_closed == True and flag_distinct == True and flag_consistent == True:
        print("Table is prepared.")
        return t, t_number
    else:
        return make_prepared(t, t_number, sigma, rta)

def make_closed(move, table, sigma, rta):
    #flag, move = table.is_closed()
    new_E = table.E
    new_R = [r for r in table.R]
    new_R.remove(move)
    new_S = [s for s in table.S]
    new_S.append(move)
    closed_table = Table(new_S, new_R, new_E)

    closed_table.update_primes()
    prime_rows = table.get_primes()

    table_tws = [s.tws for s in closed_table.S] + [r.tws for r in closed_table.R]
    
    s_tws = [tw for tw in move.tws]
    for action in sigma:
        temp_tws = s_tws+[Timedword(action,0)]
        if temp_tws not in table_tws:
            temp_element = Element(temp_tws,[])
            if temp_element.is_composed(prime_rows):
                temp_element.prime = False
            else:
                temp_element.prime = True
            fill(temp_element, closed_table.E, rta)
            temp_element.sv = temp_element.whichstate()
            closed_table.R.append(temp_element)
            table_tws = [s.tws for s in closed_table.S] + [r.tws for r in closed_table.R]
    closed_table.update_primes()
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
        new_S[i].sv = new_S[i].whichstate()
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
        new_R[j].sv = new_R[j].whichstate()
    consistent_table = Table(new_S, new_R, new_E)
    consistent_table.update_primes()
    return consistent_table

def make_evidence_closed(new_added, table, sigma, rta):
    #flag, new_added = table.is_evidence_closed()
    for i in range(0,len(new_added)):
        fill(new_added[i], table.E, rta)
        new_added[i].sv = new_added[i].whichstate()
    new_E = [e for e in table.E]
    new_R = [r for r in table.R] + [nr for nr in new_added]
    new_S = [s for s in table.S]
    evidence_closed_table = Table(new_S, new_R, new_E)
    evidence_closed_table.update_primes()
    return evidence_closed_table

def make_source_distinct(new_elements, table, rta):
    for element in new_elements:
        fill(element, table.E, rta)
        element.sv = element.whichstate()
    new_E = [e for e in table.E]
    new_R = [r for r in table.R] + [nr for nr in new_elements]
    new_S = [s for s in table.S]
    source_distinct_table = Table(new_S, new_R, new_E)
    print("Distinct done.")
    source_distinct_table.update_primes()
    return source_distinct_table

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

def suffixes(rws):
    """Return the suffixes of a regionwords. [rws1, rws2, rws3, ..., rwsn]
    """
    suffixes = []
    for i in range(0, len(rws)):
        temp_rws = rws[i:]
        suffixes.append(temp_rws)
    return suffixes

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
    """When receiving a counterexample ctx (a timedwords), add its prefixes into R and add its suffixes into E
    (except those already present in S U R and E)
    """
    pref = prefixes(ctx)
    suff = suffixes(ctx)
    S_R_tws = [s.tws for s in table.S] + [r.tws for r in table.R]
    new_S = [s for s in table.S]
    new_R = [r for r in table.R]
    # new_E = [e for e in table.E]
    new_E = [e for e in table.E] + [rws for rws in suff if rws not in table.E]
    for i in range(0, len(new_S)):
        fill(new_S[i], new_E, rta)
        new_S[i].sv = new_S[i].whichstate()
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
        new_R[j].sv = new_R[j].whichstate()
    
    for tws, j in zip(pref, range(len(pref))):
        need_add = True
        for stws in S_R_tws:
            if tws == stws:
                need_add = False
                break
        if need_add == True:
            temp_element = Element(tws,[])
            fill(temp_element, new_E, rta)
            temp_element.sv = temp_element.whichstate()
            new_R.append(temp_element)

    new_table =  Table(new_S, new_R, new_E)
    new_table.update_primes()
    print("S+R:", len(new_table.S)+len(new_table.R), "E:", len(new_table.E)+1)
    return new_table

def ctx_analysis(table, ctx, ctx_type, rta, hypothesis):
    """ Binary search to analyze the counterexample based on homing sequences process.
        Build a decomposition and return a suffix of the counterexample. The suffix will be helpful to fix the counterexample.
    """
    # query_ctx = rta.is_accept(ctx)
    query_ctx = ctx_type # The running results in teacher
    lower = 2
    upper = len(ctx) - 1
    while True:
        mid = math.floor((lower + upper) / 2)
        s = ctx[:mid-1]
        d = ctx[mid-1:]
        current_locations = hypothesis.run_tws(hypothesis.initstate_names,s)
        current_prefixes = []
        for source in current_locations:
            primes = table.get_primes()
            current_prefixes.append(primes[int(source)-1].tws + d)
        current_query = 0
        for cp in current_prefixes:
            if rta.is_accept(cp) == 1:
                current_query = 1
        if current_query != query_ctx:
            upper = mid -1
            if upper < lower:
                return ctx[mid-1:]
        else:
            lower = mid + 1
            if upper < lower:
                return ctx[mid:]

def add_ctx_new(table, ctx, ctx_type, rta, hypothesis):
    """The counterexample process by using homing sequences.
    """
    S_R_tws = [s.tws for s in table.S] + [r.tws for r in table.R]
    new_S = [s for s in table.S]
    new_R = [r for r in table.R]
    new_E = [e for e in table.E]

    new_e = ctx_analysis(table, ctx, ctx_type, rta, hypothesis)
    # print(new_e)
    # if len(new_e) == 0:
    #     new_e = ctx

    pref = prefixes(ctx)
    # new_prefix = ctx[:len(ctx)-len(new_e)]
    # pref = prefixes(new_prefix)

    if new_e != [] and new_e not in table.E:
        new_E = [e for e in table.E] + [new_e]
    # suff = suffixes(new_e)
    # new_E = [e for e in table.E] + [rws for rws in suff if rws not in table.E]

    for i in range(0, len(new_S)):
        fill(new_S[i], new_E, rta)
        new_S[i].sv = new_S[i].whichstate()
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
        new_R[j].sv = new_R[j].whichstate()

    for tws, j in zip(pref, range(len(pref))):
        need_add = True
        for stws in S_R_tws:
            if tws == stws:
                need_add = False
                break
        if need_add == True:
            temp_element = Element(tws,[])
            fill(temp_element, new_E, rta)
            temp_element.sv = temp_element.whichstate()
            new_R.append(temp_element)

    new_table =  Table(new_S, new_R, new_E)
    new_table.update_primes()
    return new_table

def add_ctx_new2(table, ctx, ctx_type, rta, hypothesis):
    """The counterexample process by using homing sequences.
    """
    S_R_tws = [s.tws for s in table.S] + [r.tws for r in table.R]
    new_S = [s for s in table.S]
    new_R = [r for r in table.R]
    new_E = [e for e in table.E]

    new_e = None
    table_elements = [s for s in table.S] + [r for r in table.R]
    epsilon_row = None
    for element in table_elements:
        if element.tws == []:
            epsilon_row = element
            break
    prime_rows = table.get_primes()
    run_prefixes = []
    for s in prime_rows:
        if s.is_covered_by(epsilon_row):
            run_prefixes.append(s.tws+ctx)
    run_result = 0
    for p in run_prefixes:
        run_result = run_result or rta.is_accept(p)
    if run_result != ctx_type:
        new_e = ctx
    else:
        new_e = ctx_analysis(table, ctx, ctx_type, rta, hypothesis)
    # print(new_e)
    # if len(new_e) == 0:
    #     new_e = ctx
    # print("new_e:",new_e)
    pref = prefixes(ctx)
    # new_prefix = ctx[:len(ctx)-len(new_e)]
    # pref = prefixes(new_prefix)

    if new_e != [] and new_e not in table.E:
        new_E = [e for e in table.E] + [new_e]
    # suff = suffixes(new_e)
    # new_E = [e for e in table.E] + [rws for rws in suff if rws not in table.E]

    for i in range(0, len(new_S)):
        fill(new_S[i], new_E, rta)
        new_S[i].sv = new_S[i].whichstate()
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
        new_R[j].sv = new_R[j].whichstate()

    for tws, j in zip(pref, range(len(pref))):
        need_add = True
        for stws in S_R_tws:
            if tws == stws:
                need_add = False
                break
        if need_add == True:
            temp_element = Element(tws,[])
            fill(temp_element, new_E, rta)
            temp_element.sv = temp_element.whichstate()
            new_R.append(temp_element)

    new_table =  Table(new_S, new_R, new_E)
    new_table.update_primes()
    return new_table