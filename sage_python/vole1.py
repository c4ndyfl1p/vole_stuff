from dataclasses import dataclass, field
from sage.all import *
from sage.structure.element import RingElement
from typing import Any
from sage.rings.polynomial.polynomial_element import Polynomial
# from agents import Prover, Verifier

# ---------------------------------------------------
# Field Setup
# ---------------------------------------------------

p = 5
r = 3

Fp = GF(p)
Fpr = Fp.extension(r, 'a')
S, t = PolynomialRing(Fpr, 't').objgen()

print(f"modulus of field is {Fpr.modulus()}")

# ---------------------------------------------------
# VOLE relation object
# ---------------------------------------------------

@dataclass
class VOLETuple:
    #random vole
    rho_u_t: Any = None # polynomial representation of u, used for opening phase
    gamma_u_delta: Any=None
    u: RingElement | None = None #random vole
    b: RingElement | None = None
    v: RingElement | None = None # random vole evaluation
    

    # witness vole
    w: RingElement | None = None # prover's actual witness
    # w_poly: RingElement | None = None # polynomial representation of witness, used for opening phase
    q: RingElement | None = None #VOLE evaluation on the witness q = v + d Delta = u Delta + b + w Delta - u Delta = w delta + b
    rho_w_t: Polynomial | None = None # 
    gamma_w_delta: RingElement | None = None

    # correction values
    correction_prover: RingElement | None = None # correction value d = w -u
    correction_verifier: RingElement | None = None # correction value d = w -u, stored on verifiers side after transmission from prover


    


    def check(self, delta: RingElement) -> bool:
        # check random vole is valid
        if self.u is None or self.b is None or self.v is None:
            return False
        return self.v == (delta * self.u) + self.b

    def __str__(self):
        return (
            f"(u={self.u}, b={self.b}, v={self.v})"
            f"(w={self.w}, b={self.b}, q={self.q})"
            f"(P correction={self.correction_prover}, V correction={self.correction_verifier})"            
            )
    
    # def __str__(self):
    #     return (
    #         f"random:  (u={self.u}, b={self.b}, v={self.v})\n"
    #         f"witness: (w={self.w}, q={self.q})\n"
    #         f"corr:    (P={self.correction_prover}, V={self.correction_verifier})\n"
    #         f"---------------------------------------------------"
    #     )
    
    # def compute_correction(self, x):
    #     self.x = x
    #     pass

    def check2(self, delta: RingElement) -> bool:
        # check if vole is valid on w
        if self.w is None or self.q is None:
            return False
    
        return self.q == (delta * self.w) + self.b


# ---------------------------------------------------
# Prover / Verifier State
# ---------------------------------------------------
@dataclass
class Prover:
    # w: list[RingElement] | None = None
    vole_tuples: list[VOLETuple] = field(default_factory=list)
    

    def add_commit(self, u, b):
        self.vole_tuples.append(VOLETuple(u=u, b=b))

    def __str__(self):
        tuples_str = "\n".join(str(t) for t in self.vole_tuples)
        return (
            "=== Prover ===\n"
            # f"witness: {self.w}\n"
            f"VOLE tuples:\n{tuples_str}"
        )
    def update_witness(self, w, index):
        """ 
         Update ith witness 
        """
        self.vole_tuples[index].w = w
        self.vole_tuples[index].rho_w_t = w*t + self.vole_tuples[index].b
        # self.vole_tuples[index].w_poly = w  # for now just set w_poly to w, in a real implementation this would be a polynomial representation of w, used for the opening phase

    def compute_correction_value_d(self, index):
        # compute correction value
        w = self.vole_tuples[index].w
        u = self.vole_tuples[index].u
        d = w - u
        return d
    
    def update_correction_value(self, d, index):
        """
        update correction avlue "d = w-u
        """
        self.vole_tuples[index].correction_prover = d
        
        


@dataclass
class Verifier:
    delta: RingElement | None = None
    vole_tuples: list[VOLETuple] = field(default_factory=list)

    def add_eval(self, v):
        self.vole_tuples.append(VOLETuple(u=None, b=None, v=v))

    def __str__(self):
        tuples_str = "\n".join(str(t) for t in self.vole_tuples)
        return (
            "=== Verifier ===\n"
            f"delta: {self.delta}\n"
            f"VOLE evaluations:\n{tuples_str}"
        )
    
    def update_correction(self, d, index):
        """
        update correction avlue "d = w-u
        """
        self.vole_tuples[index].correction_verifier = d

    
    def update_eval_with_correction(self,d,index):
        # adjust on verifiers side:
        v = self.vole_tuples[index].v # get v
        
        q = v + (self.delta * d) # adjust v with correction value d and delta to get 
        #q = v + d Delta = u Delta + b + w Delta - u Delta = w delta + b

        self.vole_tuples[index].q = q #update q in verifiers state
        self.vole_tuples[index].gamma_w_delta =q # copy into poly


# ---------------------------------------------------
# Testing
# ---------------------------------------------------

def test_evaluation(prover: Prover, verifier: Verifier):

    for i in range(len(prover.vole_tuples)):

        p_tuple = prover.vole_tuples[i]
        v_tuple = verifier.vole_tuples[i]

        vole_random = VOLETuple(u=p_tuple.u, b=p_tuple.b, v=v_tuple.v)
        vole_witness = VOLETuple(w=p_tuple.w, b=p_tuple.b, q=v_tuple.q )

        assert vole_random.check(verifier.delta),"Evaluation failed"
        assert vole_witness.check2(verifier.delta), "Evaluation with correction failed"

    print("All VOLE relations verified ✓")


# ---------------------------------------------------
# sVOLE protocol
# ---------------------------------------------------

def sVOLE(prover: Prover, verifier: Verifier, command, *args):

    if command == "Init":
        # initialise sVOLE, ie give delta to V

        delta = Fpr.random_element()
        verifier.delta = delta

        print(f"Verifier sampled Δ = {delta}")

    elif command == "sVOLE":
        # only called from commit for now

        l = args[0]
        # generate l number of random, VOLES

        print(f"Generating {l} VOLE tuples")

        for _ in range(l):

            u = Fp.random_element() # sample u

            b = Fpr.random_element() # macro auth starts here

            
            #--------- rho_u(t) = u T + b (testing rn)------------------------
            
            rho_u_t = u * t + b
            

            # verifier evaluates rho_u at delta to get v
            gamma_u_delta = rho_u_t(verifier.delta) # this is the same as u*delta + b

            v = verifier.delta * u + b

            assert gamma_u_delta == v, "Evaluation of rho_u at delta does not match expected value"
            #-----------------------------------

            prover.add_commit(u, b)
            verifier.add_eval(v)

            #-----------------------------------
            prover.vole_tuples[-1].rho_u_t = rho_u_t #experimental
            prover.vole_tuples[-1].gamma_u_delta = gamma_u_delta #experimental
            #------------------------------------

            print(f"(u={u}, b={b}, v={v}) : {v}={u}*{verifier.delta}+{b} mod {p}")


def commit(prover:Prover, verifier: Verifier, witness: list[RingElement]):
    """
    Commit phase of sVOLE protocol.
    x in [Fp, Fp...] is the list of witnesses that the prover wants to commit to, and prove knowledge of.  
    1. Generate l number of random VOLE tuples, where l is the length of the witness list.
    2. For each witness, compute correction value d = w-u
    3. P stores correction, sends to V, V stores correction.
    4. V adjusts its VOLE evaluation with the correction value, to get q = v + d Delta = u Delta + b + w Delta - u Delta = w delta + b
    """

    l = len(witness)
    #1. request l number of  random VOLE tuples
    sVOLE(prover, verifier, "sVOLE", l)

    # 2. compute correction value and send to V
    for i in range(l):
        w = witness[i]
        # add witness to prover's state
        prover.update_witness(w, i)

        # Prover computes correction value 
        d = prover.compute_correction_value_d(i)
        print(f"correction value is {d}")

        # store correction value in  provers state
        prover.update_correction_value(d, i)

        # simulate sending correction to verifer
        

        # verifier recieved d, stores d 
        verifier.update_correction(d,i)

        #verifier recomputes vole evaluation and updates it
        verifier.update_eval_with_correction(d,i)



    # 3. Adjust on V's side
    

def open(prover: Prover, verifier: Verifier, x, index):
    """
    Open phase of sVOLE protocol.
    Prover sends polynomial rho_w(t), w
    V checks if :
    1. rho_w(t) = w
    2. degree(rho_w(t)) == d 
    3. rho_w(t=Delta) = gamma_w_delta
    """

    assert index < len(prover.vole_tuples), "Invalid index for opening"
    assert index < len(verifier.vole_tuples), "Invalid index for opening"
    assert prover.vole_tuples[index].w == x, "Prover's witness does not match x"
    # need VOPES for this

    rho_w_t = prover.vole_tuples[index].rho_w_t
    assert rho_w_t.coefficients()[-1]== x, "highest degree coefficeint not equal"
    assert rho_w_t(verifier.delta) == verifier.vole_tuples[index].gamma_w_delta, "eval not equal"
    # add degree check
    
    print(f"opening of {x=} succesful")
    pass


# ---------------------------------------------------
# Run protocol
# ---------------------------------------------------

prover = Prover()
verifier = Verifier()

sVOLE(prover, verifier, "Init")

commit(prover, verifier, [Fp(3)])


# sVOLE(prover, verifier, "sVOLE", 1)

print()
print(prover)
print()
print(verifier)

test_evaluation(prover, verifier)

open(prover, verifier, Fp(3), 0)



