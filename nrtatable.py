# observation table and membership query
import math, copy
from interval import min_constraint_number
from nrta import Timedword, Location
from regionautomaton import RATran, RegionAutomaton

class Element():
    """One row in table.
    """
    def __init__(self, rws=[], value=[], sv=""):
        self.rws = rws or []
        self.value = value or []
        self.sv = sv
    
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


class Table(object):
    """Given a symbolic alphabet sigma = [a1, a2, ..., b1, b2, ...]
        R = S cdot sigma
    """
    def __init__(self, S = [], R = [], E = []):
        self.S = S
        self.R = R
        self.E = E
    
    def is_closed(self):
        rows_value = [s.value for s in self.S]
        for u in self.R:
            if u.value not in rows_value:
                return False, u
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
        table_element = [s for s in self.S] + [r for r in self.R]
        table_mapping = dict()
        for element in table_element:
            table_mapping[tuple(element.rws)] = element
        for i in range(0,len(self.S)): # u1
            for j in range(0,len(self.S)): # u2
                if i == j:
                    continue
                if self.S[j].value == self.S[i].value:
                    for regionlabel in region_alphabet_list:
                        u1_a = [rl for rl in self.S[i].rws] + [regionlabel]
                        u2_a = [rl for rl in self.S[j].rws] + [regionlabel]
                        row1 = table_mapping[tuple(u1_a)]
                        row2 = table_mapping[tuple(u2_a)]
                        if row2.value == row1.value:
                            pass
                        else:
                            flag = False
                            new_a = regionlabel
                            for k in range(len(row1.value)):
                                if row2.value[k] != row1.value[k]:
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

def make_prepared(table,t_number,region_alphabet_list,rta):
    flag_closed, move = table.is_closed()
    if flag_closed == False:
        print("Not closed")
        temp = make_closed(move, table, region_alphabet_list, rta)
        table = temp
        t_number = t_number + 1
        print("Table " + str(t_number))
        # table.show()
        print("--------------------------------------------------")
    # flag_consistent, new_a, new_e_index = table.is_consistent(region_alphabet_list)
    # if flag_consistent == False:
    #     print("Not consistent")
    #     temp = make_consistent(new_a, new_e_index, table, rta)
    #     table = temp
    #     t_number = t_number + 1
    #     print("Table " + str(t_number))
    #     # table.show()
    #     print("--------------------------------------------------")
    if flag_closed == True: # and flag_consistent == True:
        return table, t_number
    else:
        return make_prepared(table,t_number,region_alphabet_list,rta)

def make_closed(move, table, region_alphabet_list, rta):
    #flag, move = table.is_closed()
    new_E = table.E
    new_R = [r for r in table.R]
    new_R.remove(move)
    new_S = [s for s in table.S]
    new_S.append(move)
    closed_table = Table(new_S, new_R, new_E)

    table_rws = [s.rws for s in closed_table.S] + [r.rws for r in closed_table.R]
    s_rws = [tw for tw in move.rws]
    for regionlabel in region_alphabet_list:
        temp_rws = s_rws+[regionlabel]
        if temp_rws not in table_rws:
            temp_element = Element(temp_rws,[])
            fill(temp_element, closed_table.E, rta)
            temp_element.sv = temp_element.whichstate()
            closed_table.R.append(temp_element)
            # table_rws = [s.rws for s in closed_table.S] + [r.rws for r in closed_table.R]
            table_rws.append(temp_element.rws)

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
        new_S[i].sv = new_S[i].whichstate()
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
        new_R[j].sv = new_R[j].whichstate()
    consistent_table = Table(new_S, new_R, new_E)
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
            primes = table.S
            current_prefixes.append([Timedword(rl.label,min_constraint_number(rl.region)) for rl in primes[int(source)-1].rws] + d)
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

def add_ctx_new(nrtatable, rl_dict, ctx, ctx_type, rta, hypothesis):
    new_e = ctx_analysis(nrtatable, ctx, ctx_type, rta, hypothesis)
    rws = [rl_dict[tuple([tw.action,tw.time])] for tw in new_e]
    suff = suffixes(rws)
    new_S = [s for s in nrtatable.S]
    new_R = [r for r in nrtatable.R]
    new_E = [e for e in nrtatable.E] + [rws for rws in suff if rws not in nrtatable.E]
    for i in range(0, len(new_S)):
        fill(new_S[i], new_E, rta)
        new_S[i].sv = new_S[i].whichstate()
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
        new_R[j].sv = new_R[j].whichstate()
    new_table = Table(new_S, new_R, new_E)
    return new_table

def add_ctx(nrtatable, region_alphabet, rl_dict, ctx, rta):
    """When receiving a counterexample ctx (a timedwords), first transiform it to a regionwords rws and then add the suffixes of rws to E
    (except those already present in E)
    """
    rws = [rl_dict[tuple([tw.action,tw.time])] for tw in ctx]
    # for tw in ctx:
    #     for rl in region_alphabet[tw.action]:
    #         if rl.region.isininterval(tw.time):
    #             rws.append(rl)
    #             break

    suff = suffixes(rws)
    new_S = [s for s in nrtatable.S]
    new_R = [r for r in nrtatable.R]
    new_E = [e for e in nrtatable.E] + [rws for rws in suff if rws not in nrtatable.E]
    for i in range(0, len(new_S)):
        fill(new_S[i], new_E, rta)
        new_S[i].sv = new_S[i].whichstate()
    for j in range(0, len(new_R)):
        fill(new_R[j], new_E, rta)
        new_R[j].sv = new_R[j].whichstate()
    new_table = Table(new_S, new_R, new_E)
    return new_table

def table_to_ra(nrtatable, sigma, region_alphabet, n):
    """Given a prepared table, transform it to a region automaton.
    "n": the table index
    """
    region_alphabet_list = []
    for action in sigma:
        region_alphabet_list.extend(region_alphabet[action])

    table_elements = [s for s in nrtatable.S] + [r for r in nrtatable.R]
    table_mapping = dict()
    for element in table_elements:
        table_mapping[tuple(element.rws)] = element

    # Locations
    locations = []
    initstate_names = []
    accept_names = []
    value_name_dict = dict()

    for s,i in zip(nrtatable.S, range(1, len(nrtatable.S)+1)):
        name = str(i)
        value_name_dict[s.sv] = name
        init = False
        accept = False
        if s.rws == []:
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
        if u.sv in value_name_dict: # row(u) \in Q
            source = value_name_dict[u.sv]
            for a in region_alphabet_list:
                temp = [rl for rl in u.rws] + [a]
                # ua = nrtatable.findrow_by_regionwords_in_SR(temp)
                ua = table_mapping[tuple(temp)]
                target = value_name_dict[ua.sv]
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