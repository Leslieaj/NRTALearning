##
import sys,os
import time, copy
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

def learn(AA, teacher_timed_alphabet, sigma, file_pre):
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
        table, t_number = make_prepared(table, t_number, sigma, AA)
        ea = table_to_ea(table, t_number)
        eq_number = eq_number + 1
        #h_number = h_number + 1
        h_number = t_number
        h = ea_to_rta(ea,"",sigma, h_number)
        print("Hypothesis", str(eq_number), "is constructed")
        # h.show()
        target = copy.deepcopy(h)
        print("Equivalence query.")
        equivalent, ctx = equivalence_query(h, AA, teacher_timed_alphabet)
        # equivalent, ctx = equivalence_query(h, AA, region_alphabet)
        if equivalent == False:
            print("Not equivalent")
            print(ctx.tws)
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
        print("The element number of prime rows in S in the last table: " + str(len(table.get_primes())))
        print("The element number of S in the last table: " + str(len(table.S)))
        print("The element number of R in the last table: " + str(len(table.R)))
        print("The element number of E in the last table (excluding the empty-word): " + str(len(table.E)))
        print("Total number of observation table: " + str(t_number))
        print("Total number of membership query: " + str((len(table.S)+len(table.R))*(len(table.E)+1)))
        print("Total number of equivalence query: " + str(eq_number))
        print("*******************Successful !***********************")
        print(file_pre)
        folders = file_pre.split('/')
        newfolder = "".join([folder + '/' for folder in folders[:-1]])+'result/'
        if not os.path.exists(newfolder):
            print(newfolder)
            os.makedirs(newfolder)
        fname = folders[len(folders)-1].split('-')[0]
        with open(newfolder+fname + '_result.txt', 'a') as f:
            output = " ".join([str(end-start), str(len(table.S)), str(len(table.R)), str(len(table.E)), str(t_number), str((len(table.S)+len(table.R))*(len(table.E)+1)), str(eq_number), '\n'])
            f.write(output)
    return 0

def main():
    paras = sys.argv
    filename = str(paras[1])
    A,_ = buildRTA(filename)
    AA = buildAssistantRTA(A)
    sigma = AA.sigma
    file_pre,_ = filename.split(".",1)

    temp_alphabet = []
    for tran in AA.trans:
        label = tran.label
        constraint = tran.constraint
        timed_label = Timedlabel("",label,[constraint])
        if timed_label not in temp_alphabet:
            temp_alphabet += [timed_label]
    teacher_timed_alphabet = alphabet_classify(temp_alphabet, AA.sigma)
    learn(AA, teacher_timed_alphabet, sigma, file_pre)
    return 0

if __name__=='__main__':
	main()