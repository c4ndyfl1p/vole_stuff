

from sage.all import *
from sage.rings.finite_rings.element_givaro import FiniteField_givaroElement
from sage.rings.finite_rings.element_base import FiniteFieldElement
p = 17
r= 2

Fp = GF(p)        # finite field F_p
Fpr = Fp.extension(r, 'a') #or GF(p**r)
print(f"modulus of field is {Fpr.modulus()}")


#define a custpm type for Fpr
# <class 'sage.rings.finite_rings.element_givaro.FiniteField_givaroElement'>

#make a Prover class and a Verifier class for the sVOLE protocol
class Prover:
    def __init__(self):
        self.u: list = None
        self.random_commits:list = None
        self.u_commits:list = None

class Verifier:
    def __init__(self):
        self.delta: FiniteFieldElement = None
        self.random_commits_evaluated: list =None
        self.u_commits_evaluated: list = None


#make a class for the sVOLE protocol
class sVOLE:
    def __init__(self):
        self.P = Prover()
        self.V = Verifier()




def sVOLE(command):
    if command[0] == ("Init"):
        #sample Delta and gtive to verifier
        delta = Fpr.random_element()
        print(f"Delta: {delta}")
        #return delta to V
    if command[0] == "sVOLE":
        l = command[1]
        # generate l random elements u
        u = [Fp.random_element() for i in range(l)]
        print(f"u: {u}")

sVOLE(["Init"])
sVOLE(["sVOLE", 5])

        