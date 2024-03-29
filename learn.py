## The main file for batch running
import sys, os
import time, copy
from pstats import Stats
import cProfile

from nrta import buildRTA, buildAssistantRTA, Regionlabel, build_region_alphabet
from nrtatable import Element, Table, table_to_ra, add_ctx, make_closed, make_consistent, fill, make_prepared
from regionautomaton import rta_to_ra, ra_to_rta
from hkc_equivalence import equivalence_query

def init_table(region_alphabet_list, rta):
    S = [Element([],[])]
    R = []
    E = []
    for rl in region_alphabet_list:
        new_rws = [rl]
        new_element = Element(new_rws,[])
        R.append(new_element)
    for s in S:
        fill(s, E, rta)
        s.sv = s.whichstate()
    for r in R:
        fill(r, E, rta)
        r.sv = r.whichstate()
    T = Table(S, R, E)
    return T

def learn(AA, region_alphabet, sigma, file_pre):
    region_alphabet_list = []
    for action in sigma:
        region_alphabet_list.extend(region_alphabet[action])
    print("**************Start to learn ...*******************")
    start = time.time()
    T1 = init_table(region_alphabet_list, AA)
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
        table, t_number = make_prepared(table,t_number,region_alphabet_list,AA)
        ra = table_to_ra(table, sigma, region_alphabet, t_number)
        eq_number = eq_number + 1
        h_number = h_number + 1
        # h_number = t_number
        h = ra_to_rta(ra,h_number)
        print("Hypothesis " + str(eq_number) + " is construted.")
        # h.show()
        target = copy.deepcopy(h)
        print("Equivalence query.")
        equivalent, ctx = equivalence_query(h, AA, region_alphabet)
        if equivalent == False:
            print("Not equivalent")
            print(ctx.tws, ctx.value)
            temp = add_ctx(table, region_alphabet, ctx.tws, AA)
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
        # print()
        # target.show()
        # print("---------------------------------------------------")
        # print("Total time of learning: " + str(end-start))
        # print "---------------------------------------------------"
        # print "Time intervals simplification..."
        # print
        # print "The learned Canonical Real-time Automtaton: "
        # print
        # refine_rta_trans(target)
        # target.show()
        print("---------------------------------------------------")
        print("Total time: " + str(end-start) + " seconds.")
        print("The element number of prime rows in S in the last table: " + str(len(table.get_primes())))
        print("The element number of S in the last table: " + str(len(table.S)))
        print("The element number of R in the last table: " + str(len(table.R)))
        print("The element number of E in the last table (excluding the empty-word): " + str(len(table.E)))
        print("Total number of observation table: " + str(t_number))
        print("Total number of membership query: " + str((len(table.S)+len(table.R))*(len(table.E)+1)))
        print("Total number of equivalence query: " + str(eq_number))
        print("*******************Successful !***********************")
        folders = file_pre.split('/')
        newfolder = "".join([folder + '/' for folder in folders[:-1]])+'result/'
        if not os.path.exists(newfolder):
            print(newfolder)
            os.makedirs(newfolder)
        fname, case_index = folders[len(folders)-1].split('-')
        with open(newfolder+fname + '_result.txt', 'a') as f:
            output = " ".join([case_index, str(end-start), str(len(table.get_primes())), str(len(table.S)), str(len(table.R)), str(len(table.E)), str(t_number), str((len(table.S)+len(table.R))*(len(table.E)+1)), str(eq_number), '\n'])
            f.write(output)
    return 0

def main():
    # profile = False
    # if profile:
    #     pr = cProfile.Profile()
    #     pr.enable()
    
    paras = sys.argv
    filename = str(paras[1])
    # A,_ = buildRTA("test/a.json")
    A,_ = buildRTA(filename)
    AA = buildAssistantRTA(A)
    sigma = AA.sigma
    file_pre,_ = filename.split(".",1)

    region_alphabet = build_region_alphabet(sigma,AA.max_time_value())
    learn(AA, region_alphabet, sigma, file_pre)

    # if profile:
    #     p = Stats(pr)
    #     p.strip_dirs()
    #     p.sort_stats('cumtime')
    #     p.print_stats(20)

if __name__=='__main__':
	main()
