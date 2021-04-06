# Unit test for rational expressions

import unittest
import os, sys
import random
sys.path.append(os.path.abspath('..'))

from interval import Constraint
from rational import *


class RationalTest(unittest.TestCase):
    def testRational(self):
        expr = Concat(Concat(Star(Atom('a',Constraint("[7,13]"))),
                             Atom('b',Constraint("[0,1]"))),
                      Union(Atom('b',Constraint("[15,19]")),
                            Atom('a',Constraint("[3,7]"))))
        self.assertEqual(str(expr), "(a,[7,13])*.(b,[0,1]).((b,[15,19])+(a,[3,7]))")

    def testGenerateRandom(self):
        np.random.seed(1)
        expr = generateRandom(20, ['a', 'b', 'c'], 20)
        self.assertEqual(str(expr), "(a,[7,13])*.(b,[0,1]).((b,[15,19])+(a,[3,7]))")

    def testRelabel(self):
        expr = Concat(Concat(Star(Atom('a',Constraint("[7,13]"))),
                             Atom('b',Constraint("[0,1]"))),
                      Union(Atom('b',Constraint("[15,19]")),
                            Atom('a',Constraint("[3,7]"))))
        expr, final_index = relabel(expr, 1)
        self.assertEqual(repr(expr),
        """Concat(Concat(Star(Atom('a',Constraint("[7,13]"),2)),Atom('b',Constraint("[0,1]"),3)),Union(Atom('b',Constraint("[15,19]"),4),Atom('a',Constraint("[3,7]"),5)))""")
        self.assertEqual(final_index, 5)

    def testGets(self):
        expr = Concat(Concat(Star(Atom('a',Constraint("[7,13]"))),
                             Atom('b',Constraint("[0,1]"))),
                      Union(Atom('b',Constraint("[15,19]")),
                            Atom('a',Constraint("[3,7]"))))
        expr, final_index = relabel(expr, 1)
        self.assertEqual(getLambda(expr), False)
        self.assertEqual(getP(expr), {Atom('a',Constraint("[7,13]"),2), Atom('b',Constraint("[0,1]"),3)})
        self.assertEqual(getD(expr), {Atom('b',Constraint("[15,19]"),4), Atom('a',Constraint("[3,7]"),5)})
        self.assertEqual(getF(expr), {
            (Atom('b',Constraint("[0,1]"),3), Atom('b',Constraint("[15,19]"),4)),
            (Atom('b',Constraint("[0,1]"),3), Atom('a',Constraint("[3,7]"),5)),
            (Atom('a',Constraint("[7,13]"),2), Atom('a',Constraint("[7,13]"),2)),
            (Atom('a',Constraint("[7,13]"),2), Atom('b',Constraint("[0,1]"),3))
        })

    def testExprToRTA(self):
        expr = Concat(Concat(Star(Atom('a',Constraint("[7,13]"))),
                             Atom('b',Constraint("[0,1]"))),
                      Union(Atom('b',Constraint("[15,19]")),
                            Atom('a',Constraint("[3,7]"))))
        expr, final_index = relabel(expr, 1)
        rta = exprToRTA(expr, "1", ["a", "b", "c"], final_index)
        # rta.show()

    def testRandom(self):
        np.random.seed(1)
        for i in range(10):
            expr = generateRandom(20, ['a', 'b', 'c'], 20)
            expr, final_index = relabel(expr, 1)
            rta = exprToRTA(expr, "1", ["a", "b", "c"], final_index)
            # rta.show()


if __name__ == "__main__":
    unittest.main()
