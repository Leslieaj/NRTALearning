import unittest
import sys
sys.path.append('../')

from interval import Constraint
from nrta import Timedword, Regionlabel, buildRTA, buildAssistantRTA, build_region_alphabet

A, _ = buildRTA('a.json')
AA = buildAssistantRTA(A)  # Assist

tws0 = []
tws1 = [Timedword('a',1), Timedword('b',1)]
tws2 = [Timedword('a',2), Timedword('a',6)]
tws3 = [Timedword('a',2), Timedword('a',4)]
tws4 = [Timedword('a',2.5), Timedword('b',6)]
tws5 = [Timedword('a',2.5), Timedword('b',0)]
tws6 = [Timedword('a',2.5), Timedword('b',1.5), Timedword('a',2.1), Timedword('b',3.5)]
tws7 = [Timedword('a',2.5), Timedword('b',1.5), Timedword('a',2.1), Timedword('b',3)]
tws8 = [Timedword('a',2.5), Timedword('b',1.5), Timedword('a',2.1), Timedword('b',3.5), Timedword('a',2)]
tws9 = [Timedword('a',2.5), Timedword('b',1.5), Timedword('a',2.1), Timedword('b',3.5), Timedword('a',2), Timedword('b',3.5)]

rws0 = []
rws1 = [Regionlabel(2,'a',Constraint("[1,1]")), Regionlabel(2,'b',Constraint("[1,1]"))]
rws2 = [Regionlabel(4,'a',Constraint("[2,2]")), Regionlabel(12,'a',Constraint("[6,6]"))]
rws3 = [Regionlabel(4,'a',Constraint("[2,2]")), Regionlabel(8,'a',Constraint("[4,4]"))]
rws4 = [Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(12,'a',Constraint("[6,6]"))]
rws5 = [Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(0,'b',Constraint("[0,0]"))]
rws6 = [Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(3,'b',Constraint("(1,2)")), Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(7,'b',Constraint("(3,4)"))]
rws7 = [Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(3,'b',Constraint("(1,2)")), Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(6,'b',Constraint("[3,3]"))]
rws8 = [Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(3,'b',Constraint("(1,2)")), Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(7,'b',Constraint("(3,4)")), Regionlabel(4,'a',Constraint("[2,2]"))]
rws9 = [Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(3,'b',Constraint("(1,2)")), Regionlabel(5,'a',Constraint("(2,3)")), Regionlabel(7,'b',Constraint("(3,4)")), Regionlabel(4,'a',Constraint("[2,2]")), Regionlabel(7,'b',Constraint("(3,4)"))]

class EquivalenceTest(unittest.TestCase):
    def test_max_time_value(self):
        self.assertEqual(AA.max_time_value(), 9)
    
    def test_is_accept(self):
        self.assertEqual(AA.is_accept(tws0), False)
        self.assertEqual(AA.is_accept(tws1), False)
        self.assertEqual(AA.is_accept(tws2), True)
        self.assertEqual(AA.is_accept(tws3), False)
        self.assertEqual(AA.is_accept(tws4), True)
        self.assertEqual(AA.is_accept(tws5), False)
        self.assertEqual(AA.is_accept(tws6), True)
        self.assertEqual(AA.is_accept(tws7), False)
        self.assertEqual(AA.is_accept(tws8), False)
        self.assertEqual(AA.is_accept(tws9), True)
    
    def test_is_accept_rws(self):
        self.assertEqual(AA.is_accept_rws(rws0), False)
        self.assertEqual(AA.is_accept_rws(rws1), False)
        self.assertEqual(AA.is_accept_rws(rws2), True)
        self.assertEqual(AA.is_accept_rws(rws3), False)
        self.assertEqual(AA.is_accept_rws(rws4), True)
        self.assertEqual(AA.is_accept_rws(rws5), False)
        self.assertEqual(AA.is_accept_rws(rws6), True)
        self.assertEqual(AA.is_accept_rws(rws7), False)
        self.assertEqual(AA.is_accept_rws(rws8), False)
        self.assertEqual(AA.is_accept_rws(rws9), True)
    
    def test_build_region_alphabet(self):
        sigma1 = ["a","b"]
        max_time_value_1 = 0
        max_time_value_2 = 2
        max_time_value_3 = 9

        region_alphabet1 = build_region_alphabet(sigma1, max_time_value_1)
        self.assertEqual(region_alphabet1, {"b": [Regionlabel(0,"b",Constraint("[0,0]")),Regionlabel(1,"b",Constraint("(0,+)"))], "a": [Regionlabel(0,"a",Constraint("[0,0]")),Regionlabel(1,"a",Constraint("(0,+)"))]})
        
        b0 = Regionlabel(0,"b",Constraint("[0,0]"))
        b1 = Regionlabel(1,"b",Constraint("(0,1)"))
        b2 = Regionlabel(2,"b",Constraint("[1,1]"))
        b3 = Regionlabel(3,"b",Constraint("(1,2)"))
        b4 = Regionlabel(4,"b",Constraint("[2,2]"))
        b5 = Regionlabel(5,"b",Constraint("(2,+)"))

        a0 = Regionlabel(0,"a",Constraint("[0,0]"))
        a1 = Regionlabel(1,"a",Constraint("(0,1)"))
        a2 = Regionlabel(2,"a",Constraint("[1,1]"))
        a3 = Regionlabel(3,"a",Constraint("(1,2)"))
        a4 = Regionlabel(4,"a",Constraint("[2,2]"))
        a5 = Regionlabel(5,"a",Constraint("(2,+)"))

        region_alphabet2 = build_region_alphabet(sigma1, max_time_value_2)
        self.assertEqual(region_alphabet2, {"a":[a0,a1,a2,a3,a4,a5], "b":[b0,b1,b2,b3,b4,b5]})

        region_alphabet3 = build_region_alphabet(sigma1, max_time_value_3)
        self.assertEqual(len(region_alphabet3["a"]), 20)
        self.assertEqual(len(region_alphabet3["b"]), 20)


if __name__ == "__main__":
    unittest.main()