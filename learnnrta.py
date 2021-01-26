##
from nrta import buildRTA, buildAssistantRTA, Timedword
from fa import Timedlabel, alphabet_classify
from observation import Element, Table, add_ctx, make_closed, make_consistent
from hypothesis import table_to_ea, ea_to_rta
from equivalence import equivalence_query


def main():
    A,_ = buildRTA("test/a.json")
    AA = buildAssistantRTA(A)
    sigma = ["a", "b"]

    temp_alphabet = []
    for tran in AA.trans:
        label = tran.label
        constraint = tran.constraint
        timed_label = Timedlabel("",label,[constraint])
        if timed_label not in temp_alphabet:
            temp_alphabet += [timed_label]
    teacher_timed_alphabet = alphabet_classify(temp_alphabet, AA.sigma)

    tw1 = Timedword("a", 0)
    tw2 = Timedword("b", 0)
    tws0 = [] # empty
    tws1 = [tw1] # (a,0)
    tws2 = [tw2] # (b,0)
    e0 = Element(tws0,[0])
    e0.prime = True
    e1 = Element(tws1,[0])
    e2 = Element(tws2,[0])

    print("-------------T 1--------------------")
    S = [e0]
    R = [e1,e2]
    E = []
    T1 = Table(S,R,E)
    T1.show()
    print("-------------EA 1-------------------")
    ea1 = table_to_ea(T1,1)
    ea1.show()
    print("-------------H 1--------------------")
    h1 = ea_to_rta(ea1,"",sigma,1)
    h1.show()
    print("-------------T 2-------------------")
    eq1, ctx1 = equivalence_query(h1, A, teacher_timed_alphabet)
    print(eq1, ctx1.tws, ctx1.value)
    T2 = add_ctx(T1, ctx1.tws, A)
    T2.show()
    closed_flag, move = T2.is_closed()
    print(closed_flag, move.tws, move.value)
    T2 = make_closed(move, T2, sigma, AA)
    T2.show()
    closed_flag, move = T2.is_closed()
    print(closed_flag)
    consistent_flag, new_a, new_e_index = T2.is_consistent()
    print(consistent_flag, new_a, new_e_index)
    print("-------------EA 2-----------------------")
    ea2 = table_to_ea(T2,2)
    ea2.show()
    print("-------------H 2-----------------------")
    h2 = ea_to_rta(ea2,"",sigma,2)
    h2.show()
    print("------------T 3------------------------")
    eq2, ctx2 = equivalence_query(h2, A, teacher_timed_alphabet)
    print(eq2, ctx2.tws, ctx2.value)
    T3 = add_ctx(T2, ctx2.tws, A)
    T3.show()
    closed_flag, move = T3.is_closed()
    print(closed_flag)
    consistent_flag, new_a, new_e_index = T3.is_consistent()
    print(consistent_flag, new_a, new_e_index)
    print("-------------EA 3-----------------------")
    ea3 = table_to_ea(T3,3)
    ea3.show()
    print("-------------H 3-----------------------")
    h3 = ea_to_rta(ea3,"",sigma,3)
    h3.show()
    print("------------T 4------------------------")
    eq3, ctx3 = equivalence_query(h3, AA, teacher_timed_alphabet)
    print(eq3, ctx3.tws, ctx3.value)
    T4 = add_ctx(T3, ctx3.tws, AA)
    T4.show()
    closed_flag, move = T4.is_closed()
    print(closed_flag)
    consistent_flag, new_a, new_e_index = T4.is_consistent()
    print(consistent_flag, new_a, new_e_index)
    T4 = make_consistent(new_a, new_e_index, T4, sigma, AA)
    T4.show()
    closed_flag, move = T4.is_closed()
    print(closed_flag, move.tws, move.value)
    T4 = make_closed(move, T4, sigma, AA)
    T4.show()



if __name__=='__main__':
	main()