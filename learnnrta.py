##
import sys
import time, copy
from nrta import buildRTA, buildAssistantRTA, Regionlabel, build_region_alphabet
from nrtatable import Element, Table, table_to_ra, add_ctx, make_closed, make_consistent, fill
from regionautomaton import rta_to_ra, ra_to_rta
from equivalence import equivalence_query

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
    for r in R:
        fill(r, E, rta)
    T = Table(S, R, E)
    return T

def learn(AA, region_alphabet, sigma):
    region_alphabet_list = []
    for action in sigma:
        region_alphabet_list.extend(region_alphabet[action])
    print("**************Start to learn ...*******************")
    start = time.time()
    T1 = init_table(region_alphabet_list, AA)
    T1.update_primes()
    t_number = 1
    print("Table " + str(t_number) + " is as follow.")
    T1.show()
    print("--------------------------------------------------")
    
    equivalent = False
    table = copy.deepcopy(T1)
    h_number = 0
    eq_number = 0
    target = None
    while equivalent == False:
        prepared = table.is_prepared(region_alphabet_list)
        while prepared == False:
            flag_closed, move = table.is_closed()
            if flag_closed == False:
                print("Not closed")
                temp = make_closed(move, table, region_alphabet_list, AA)
                table = temp
                t_number = t_number + 1
                print("Table " + str(t_number) + " is as follow.")
                table.show()
                print("--------------------------------------------------")
            flag_consistent, new_a, new_e_index = table.is_consistent(region_alphabet_list)
            if flag_consistent == False:
                print("Not consistent")
                temp = make_consistent(new_a, new_e_index, table, AA)
                table = temp
                t_number = t_number + 1
                print("Table " + str(t_number) + " is as follow.")
                table.show()
                print("--------------------------------------------------")
            prepared = table.is_prepared(region_alphabet_list)
        ra = table_to_ra(table, sigma, region_alphabet, t_number)
        eq_number = eq_number + 1
        h_number = h_number + 1
        # h_number = t_number
        h = ra_to_rta(ra,h_number)
        h.show()
        target = copy.deepcopy(h)
        equivalent, ctx = equivalence_query(h, AA, region_alphabet)
        if equivalent == False:
            print("Not equivalent")
            print(ctx.tws)
            temp = add_ctx(table, region_alphabet, ctx.tws, AA)
            table = temp
            t_number = t_number + 1
            print("Table " + str(t_number) + " is as follow.")
            table.show()
            print("--------------------------------------------------")
    end = time.time()
    if target is None:
        print("Error! Learning Failed.")
        print("*******************Failed .***********************")
    else:
        print("Succeed! The learned RTA is as follows.")
        print()
        target.show()
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
        print("Total time: " + str(end-start))
        print("The element number of S in the last table: " + str(len(table.S)))
        print("The element number of R in the last table: " + str(len(table.R)))
        print("The element number of E in the last table (excluding the empty-word): " + str(len(table.E)))
        print("Total number of observation table: " + str(t_number))
        print("Total number of membership query: " + str((len(table.S)+len(table.R))*(len(table.E)+1)))
        print("Total number of equivalence query: " + str(eq_number))
        print("*******************Successful !***********************")
        # folder,fname = file_pre.split('/')
        # with open(folder+'/result/'+fname + '_result.txt', 'w') as f:
        #     output = " ".join([str(end-start), str(len(table.S)), str(len(table.R)), str(len(table.E)), str(t_number), str((len(table.S)+len(table.R))*(len(table.E)+1)), str(eq_number), '\n'])
        #     f.write(output)
    return 0

def main():
    paras = sys.argv
    filename = str(paras[1])
    # A,_ = buildRTA("test/a.json")
    A,_ = buildRTA(filename)
    AA = buildAssistantRTA(A)
    sigma = AA.sigma

    region_alphabet = build_region_alphabet(sigma,AA.max_time_value())
    learn(AA, region_alphabet, sigma)



if __name__=='__main__':
	main()