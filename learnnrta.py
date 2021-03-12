##
import sys
import time, copy
from pstats import Stats
import cProfile

from nrta import buildRTA, buildAssistantRTA, Timedword, refine_rta_trans, build_region_alphabet 
from fa import Timedlabel, alphabet_classify
from observation import Element, Table, add_ctx, make_closed, make_consistent, make_evidence_closed, make_source_distinct, fill, add_ctx_new, make_prepared
from hypothesis import table_to_ea, ea_to_rta
# from equivalence import equivalence_query
from hkc_equivalence import equivalence_query


def init_table(sigma, rta):
    S = [Element([],[])]
    R = []
    E = []
    for action in sigma:
        new_tw = Timedword(action, 0)
        new_element = Element([new_tw],[])
        R.append(new_element)
    for s in S:
        fill(s, E, rta)
        s.sv = s.whichstate()
    for r in R:
        fill(r, E, rta)
        r.sv = r.whichstate()
    T = Table(S, R, E)
    return T

def learn(AA, teacher_timed_alphabet, sigma):
# def learn(AA, region_alphabet, sigma):
    # region_alphabet_list = []
    # for action in sigma:
    #     region_alphabet_list.extend(region_alphabet[action])
    print("**************Start to learn ...*******************")
    start = time.time()
    T1 = init_table(sigma, AA)
    T1.update_primes()
    t_number = 1
    print("Table " + str(t_number))
    # T1.show()
    print("--------------------------------------------------")
    
    equivalent = False
    table = copy.deepcopy(T1)
    h_number = 0
    eq_number = 0
    target = None
    while equivalent == False:
        # prepared = table.is_prepared()
        # while prepared == False:
        #     flag_closed, move = table.is_closed()
        #     if flag_closed == False:
        #         print("Not closed")
        #         temp = make_closed(move, table, sigma, AA)
        #         table = temp
        #         t_number = t_number + 1
        #         print("Table " + str(t_number))
        #         # table.show()
        #         print("--------------------------------------------------")
        #     flag_consistent, new_a, new_e_index = table.is_consistent()
        #     if flag_consistent == False:
        #         print("Not consistent")
        #         temp = make_consistent(new_a, new_e_index, table, sigma, AA)
        #         table = temp
        #         t_number = t_number + 1
        #         print("Table " + str(t_number))
        #         # table.show()
        #         print("--------------------------------------------------")
        #     # flag_evi_closed, new_added = table.is_evidence_closed()
        #     # if flag_evi_closed == False:
        #     #     print("Not evidence closed")
        #     #     temp = make_evidence_closed(new_added, table, sigma, AA)
        #     #     table = temp
        #     #     t_number = t_number + 1
        #     #     print("Table " + str(t_number))
        #     #     # table.show()
        #     #     print("--------------------------------------------------")
        #     flag_distinct, new_elements = table.is_source_distinct()
        #     if flag_distinct == False:
        #         print("Not source distinct")
        #         temp = make_source_distinct(new_elements, table, AA)
        #         table = temp
        #         t_number = t_number + 1
        #         print("Table " + str(t_number))
        #         # table.show()
        #         print("--------------------------------------------------")
        #     prepared = table.is_prepared()
        table = make_prepared(table, t_number, sigma, AA)
        # table.show()
        ea = table_to_ea(table, t_number)
        eq_number = eq_number + 1
        #h_number = h_number + 1
        h_number = t_number
        h = ea_to_rta(ea,"",sigma, h_number)
        print("Hypothesis", str(eq_number), "is constructed")
        # h.show()
        target = copy.deepcopy(h)
        print("Equivalence query.")
        # if eq_number == 31:
        #     h.show()
        #     for s, i in zip(table.get_primes(), range(len(table.get_primes()))):
        #         if s.is_covered_by(table.S[5]):
        #             print(i+1)
            
        #     print("-----------------------------------vvvv")
        #     flag_consistent, new_a, new_e_index = table.is_consistent()
        #     equivalent, ctx = equivalence_query(h, AA, teacher_timed_alphabet)
        #     h.run_tws(h.initstate_names,ctx.tws)
        #     print(h.is_accept(ctx.tws))
        #     print()
        #     for element in table.S + table.R:
        #         if element.tws == []:
        #             continue
        #         if element.tws[-1] == Timedword("b", 10.1):
        #             if element.prime == True:
        #                 for p, i in zip(table.get_primes(), range(len(table.get_primes()))):
        #                     if p.value == element.value:
        #                         print(element.tws, element.prime, i+1)
        #                         break
        #             else:
        #                 l = []
        #                 for p, i in zip(table.get_primes(), range(len(table.get_primes()))):
        #                     if p.is_covered_by(element):
        #                         l.append(i)
        #                 print(element.tws, element.prime, l)
        #     print()
        #     for element in table.S + table.R:
        #         if element.tws == []:
        #             continue
        #         if element.tws[-1] == Timedword("b", 17):
        #             if element.prime == True:
        #                 for p, i in zip(table.get_primes(), range(len(table.get_primes()))):
        #                     if p.value == element.value:
        #                         print(element.tws, element.prime, i+1)
        #                         break
        #             else:
        #                 l = []
        #                 for p, i in zip(table.get_primes(), range(len(table.get_primes()))):
        #                     if p.is_covered_by(element):
        #                         l.append(i+1)
        #                 print(element.tws, element.prime, l)
        #     print()
        #     for element in table.S + table.R:
        #         if element.tws == []:
        #             continue
        #         if element.tws[-1] == Timedword("a", 1.1):
        #             if element.prime == True:
        #                 for p, i in zip(table.get_primes(), range(len(table.get_primes()))):
        #                     if p.value == element.value:
        #                         print(element.tws, element.prime, i+1)
        #                         break
        #             else:
        #                 l = []
        #                 for p, i in zip(table.get_primes(), range(len(table.get_primes()))):
        #                     if p.is_covered_by(element):
        #                         l.append(i+1)
        #                 print(element.tws, element.prime, l)
        #     return -1
        equivalent, ctx = equivalence_query(h, AA, teacher_timed_alphabet)
        # equivalent, ctx = equivalence_query(h, AA, region_alphabet)
        if equivalent == False:
            print("Not equivalent")
            print(ctx.tws, ctx.value)
            temp = add_ctx(table, ctx.tws, AA)
            # temp = add_ctx_new(table,ctx.tws,AA,target)
            table = temp
            t_number = t_number + 1
            print("Table " + str(t_number))
            # table.show()
            print("--------------------------------------------------")
    end = time.time()
    if target is None:
        print("Error! Learning Failed.")
        print("*******************Failed .***********************")
    else:
        print("Succeed! The learned RTA is as follows.")
        print()
        target.show()
        print("---------------------------------------------------")
        print("Total time of learning: " + str(end-start))
        print("---------------------------------------------------")
        print("Transitions simplification...")
        print("---------------------------------------------------")
        print("The learned Canonical Residual Real-time Automtaton: ")
        print("---------------------------------------------------")
        rrta = refine_rta_trans(target)
        rrta.show()
        print("---------------------------------------------------")
        print("Total time: " + str(end-start))
        print("The element number of S in the last table: " + str(len(table.S)))
        print("The element number of R in the last table: " + str(len(table.R)))
        print("The element number of E in the last table (excluding the empty-word): " + str(len(table.E)))
        print("Total number of observation table: " + str(t_number))
        print("Total number of membership query: " + str((len(table.S)+len(table.R))*(len(table.E)+1)))
        print("Total number of equivalence query: " + str(eq_number))
        print("*******************Successful !***********************")

    return 0

def main():
    profile = True
    if profile:
        pr = cProfile.Profile()
        pr.enable()

    paras = sys.argv
    filename = str(paras[1])
    A,_ = buildRTA(filename)
    # A,_ = buildRTA("test/a.json")
    AA = buildAssistantRTA(A)
    # sigma = ["a", "b"]
    sigma = AA.sigma

    temp_alphabet = []
    for tran in AA.trans:
        label = tran.label
        constraint = tran.constraint
        timed_label = Timedlabel("",label,[constraint])
        if timed_label not in temp_alphabet:
            temp_alphabet += [timed_label]
    teacher_timed_alphabet = alphabet_classify(temp_alphabet, AA.sigma)
    learn(AA, teacher_timed_alphabet, sigma)
    # region_alphabet = build_region_alphabet(sigma,AA.max_time_value())
    # learn(AA, region_alphabet, sigma)

    if profile:
        p = Stats(pr)
        p.strip_dirs()
        p.sort_stats('cumtime')
        p.print_stats(100)


    return 0

if __name__=='__main__':
	main()