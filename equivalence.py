# Equivalence query
import sys
from interval import *
from nrta import Timedword, buildRTA, buildAssistantRTA, build_region_alphabet
from regionautomaton import rta_to_ra, ra_to_rta, nfa_to_dfa, completed_dfa_complement, rfa_product
#from fa import Timedlabel, alphabet_classify, rta_to_fa, fa_to_rta, nfa_to_dfa, alphabet_combine, alphabet_partitions, completed_dfa_complement, rfa_product

class Counterexample(object):
    def __init__(self, tws = [], value = -2):
        self.tws = tws
        self.value = value

def findpath(rta, paths):
    """Find paths one more step.
    """
    current_paths = [path for path in paths]
    onemorestep_paths = []
    for path in current_paths:
        for tran in rta.trans:
            temp_path = copy.deepcopy(path)
            if tran.source == path[len(path)-1]:
                temp_path.append(tran.target)
                onemorestep_paths.append(temp_path)
    return onemorestep_paths

def buildctx(rta, path, value):
    """
        The input path can reach a accept state.
        We build a ctx depending on the path.
    """
    tws = []
    for i in range(0, len(path)-1):
        for tran in rta.trans:
            if tran.source == path[i] and tran.target == path[i+1]:
                action = tran.label
                time = min_constraint_number(tran.constraint)
                tw = Timedword(action, time)
                tws.append(tw)
                break
    ctx = Counterexample(tws,value)
    return ctx
                
def findctx(rta, value):
    """
        1. find a counter example: a accept path of rta.
        2. the value is 0 or 1, it depends that if teacher do complement, it is 0.
    """
    ctx = Counterexample([],value)
    if len(rta.locations) == 0 or len(rta.accept_names) == 0:
        return ctx
    else:
        initpath = rta.initstate_names
        current_paths = [initpath]
        #the length of the longest path is less than states numbers
        step = len(rta.locations)-1
        while(step > 0):
            new_paths = findpath(rta, current_paths)
            step = step - 1
            current_paths = [p for p in new_paths]
            for path in new_paths:
                if path[len(path)-1] in rta.accept_names:
                    #print path
                    ctx = buildctx(rta, path, value)
                    return ctx
    return ctx

def equivalence_query(hypothesis, teacher, region_alphabet):
    """hypothesis : the current nondeterministic real-time automaton hypothesis
    teacher: the real-time automaton hold by teacher
    """
    hypo_nfa = rta_to_ra(hypothesis,region_alphabet)
    teacher_nfa = rta_to_ra(teacher,region_alphabet)
    hypo_dfa = nfa_to_dfa(hypo_nfa)
    teacher_dfa = nfa_to_dfa(teacher_nfa)

    equivalent = False
    # first, computing positive examples
    comp_hypo_dfa = completed_dfa_complement(hypo_dfa)
    product_pos = rfa_product(comp_hypo_dfa,teacher_dfa)
    product_pos_rta = ra_to_rta(product_pos)
    ctx_pos = findctx(product_pos_rta, 1)
    # if no positive example, computing negtive examples
    if len(ctx_pos.tws) == 0:
        comp_teacher_dfa = completed_dfa_complement(teacher_dfa)
        product_neg = rfa_product(hypo_dfa,comp_teacher_dfa)
        product_neg_rta = ra_to_rta(product_neg)
        ctx_neg = findctx(product_neg_rta, 0)
        # if also no negtive example, then they are equivalent
        if len(ctx_neg.tws) == 0:
            equivalent = True
            return equivalent, Counterexample([],-2)
        else:
            return equivalent, ctx_neg
    else:
        return equivalent, ctx_pos
    
    # print(len(ctx_neg.tws), ":", ctx_neg.tws)
    # print(len(ctx_pos.tws), ":", ctx_pos.tws)
    # if len(ctx_neg.tws) == 0 and len(ctx_pos.tws) == 0:
    #     print("EQ:", True)
    # else:
    #     print("EQ:", False)

# def equivalence_query(hypothesis, fa):
#     hdfa = rta_to_fa(hypothesis, "receiving")
#     combined_alphabet = alphabet_combine(hdfa.timed_alphabet, fa.timed_alphabet)
#     alphapartitions,_ = alphabet_partitions(combined_alphabet)
#     refined_hdfa = fa_to_rfa(hdfa, alphapartitions)
#     refined_fa = fa_to_rfa(fa, alphapartitions)
#     comp_rhdfa = rfa_complement(refined_hdfa)
#     comp_rfa = rfa_complement(refined_fa)
#     #product_neg = clean_rfa(rfa_product(refined_hdfa, comp_rfa))
#     #product_pos = clean_rfa(rfa_product(comp_rhdfa, refined_fa))
#     product_neg = rfa_product(refined_hdfa, comp_rfa)
#     product_pos = rfa_product(comp_rhdfa, refined_fa)
#     product_neg_rta = rfa_to_rta(product_neg)
#     product_pos_rta = rfa_to_rta(product_pos)
#     ctx_neg = findctx(product_neg_rta, 0)
#     ctx_pos = findctx(product_pos_rta, 1)
#     ctx = Element([],[])
#     equivalent = False
#     if len(ctx_neg.tws) == 0 and len(ctx_pos.tws) == 0:
#         equivalent = True
#     elif len(ctx_neg.tws) != 0 and len(ctx_pos.tws) == 0:
#         ctx = ctx_neg
#     elif len(ctx_neg.tws) == 0 and len(ctx_pos.tws) != 0:
#         ctx = ctx_pos
#     else:
#         flag = random.randint(0,1)
#         if flag == 0:
#             ctx = ctx_neg
#         else:
#             ctx = ctx_pos
#     return equivalent, ctx

def main():
    print("---------------------a.json----------------")
    paras = sys.argv
    A,_ = buildRTA("test/a.json")
    print("------------------Assist-----------------")
    AA = buildAssistantRTA(A)

    B,_ = buildRTA("test/b.json")
    BB = buildAssistantRTA(B)

    region_alphabet = build_region_alphabet(AA.sigma,AA.max_time_value())

    equivalent, ctx = equivalence_query(BB, AA, region_alphabet)
    print(equivalent)
    print(ctx.tws, ctx.value)
    

if __name__=='__main__':
	main()