#Unit tests for interval.py

import unittest
import sys
sys.path.append('../')

from interval import *

c1 = Constraint("(1,4)")
c2 = Constraint("(2,6]")
c3 = Constraint("(4,5]")
c4 = Constraint("[0,1)")
c5 = Constraint("(0,3)")
c6 = Constraint("[2,5)")
c7 = Constraint("[0,+)")

class EquivalenceTest(unittest.TestCase):
    def test_unintersect_intervals(self):
        unintervals = unintersect_intervals([c1,c2,c6])
        self.assertEqual(unintervals, [Constraint("(1,6]")])

        unintervals = unintersect_intervals([c1,c3,c4])
        self.assertEqual(unintervals, [Constraint("[0,1)"),Constraint("(1,4)"),Constraint("(4,5]")])

        unintervals = unintersect_intervals([c3,c4,c5])
        self.assertEqual(unintervals, [Constraint("[0,3)"),Constraint("(4,5]")])

    def test_complement_intervals(self):
        cointervals = complement_intervals([c3,c4,c5])
        self.assertEqual(cointervals, [Constraint("[3,4]"),Constraint("(5,+)")])

        cointervals = complement_intervals([c1,c2,c6])
        self.assertEqual(cointervals, [Constraint("[0,1]"),Constraint("(6,+)")])

        cointervals = complement_intervals([c1,c3,c4])
        self.assertEqual(cointervals, [Constraint("[1,1]"),Constraint("[4,4]"),Constraint("(5,+)")])

        cointervals = complement_intervals([c1,c2,c6,c7])
        self.assertEqual(cointervals, [])

if __name__ == "__main__":
    unittest.main()