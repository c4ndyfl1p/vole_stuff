
from dataclasses import dataclass
from sage.all import *
from sage.structure.element import RingElement
from typing import Any

p = 5
r= 3

Fp = GF(p)        # finite field F_p
Fpr = Fp.extension(r, 'a') #or GF(p**r)
print(f"modulus of field is {Fpr.modulus()}")

@dataclass
#assumed degree 1 VOLE correlation for now
class Ucommit:
    u: RingElement
    b: RingElement

class UcommitEval:
    u_eval: RingElement #verifeier's value v

#make a Prover class and a Verifier class for the sVOLE protocol
@dataclass
class Prover:
    def __init__(self):
        self.w: list = None # list of P's input(witness)
        self.u_commits: list[Ucommit] =[] #list of random commits
        self.w_commits:list = [] #list of valid commits on P's inputs

    def __str__(self):
        return f"Prover(w={self.w}, u_commits={self.u_commits}, w_commits={self.w_commits})"


@dataclass
class Verifier:
    def __init__(self):
        self.delta = None
        self.u_commits_evaluated: list =[]
        self.w_commits_evaluated: list = []

    def __str__(self):
        return f"Verifier(delta={self.delta}, u_commits_evaluated={self.u_commits_evaluated}, w_commits_evaluated={self.w_commits_evaluated})"


# #make a class for the sVOLE protocol
# class sVOLE:
#     def __init__(self):
#         self.P = Prover()
#         self.V = Verifier()


def test_evaluation(prover, verifier):
    for i in range(len(prover.u_commits)):
        u, b = prover.u_commits[i]
        v = verifier.u_commits_evaluated[i]
        assert v == verifier.delta * u + b, "Evaluation failed for random VOLES"


def sVOLE(prover:Prover, verifier:Verifier, command, *args):
    if command == "Init":
        #sample Delta and gtive to verifier
        delta = Fpr.random_element()
        print(f"verifier's Delta: {delta}")

        #return delta to V
        verifier.delta = delta
    if command == "sVOLE":
        l = args[0]
        # generate l random elements u
        u = [Fp.random_element() for i in range(l)]
        print(f"Generated VOLE u: {u}")

        #run Macro(auth) and return ut+b and u Del+v
        #__auth__ (refactor later)
        b = [Fpr.random_element() for i in range(l)]
        print(f"Generated VOLE b: {b}")

        v = []
        for i in range(l):            
            v_= verifier.delta * u[i] +b[i] 
            print(v_)
            v.append(v_)

            prover.u_commits.append(Ucommit(u[i],b[i]))
            verifier.u_commits_evaluated.append(UcommitEval( v[i]))
        




prover = Prover()
verifier = Verifier()

sVOLE(prover, verifier, "Init")
sVOLE(prover, verifier, "sVOLE", 10)

print(prover)
print(verifier)

test_evaluation(prover, verifier)
