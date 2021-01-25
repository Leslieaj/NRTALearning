##
from nrta import buildRTA, buildAssistantRTA, Timedword
from observation import Element, Table

def main():
    A,_ = buildRTA("test/a.json")
    AA = buildAssistantRTA(A)
    sigma = ["a", "b"]

    tw1 = Timedword("a", 0)
    tw2 = Timedword("b", 0)
    tws0 = [] # empty
    tws1 = [tw1] # (a,0)
    tws2 = [tw2] # (b,0)
    e0 = Element(tws0,[0])
    e0.prime = True
    e1 = Element(tws1,[0])
    e2 = Element(tws2,[0])

    S = [e0]
    R = [e1,e2]
    E = []
    T = Table(S,R,E)

    





if __name__=='__main__':
	main()