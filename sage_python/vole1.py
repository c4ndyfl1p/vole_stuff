from dataclasses import dataclass, field
from typing import TypeAlias

from sage.all import GF, PolynomialRing
from sage.structure.element import RingElement
from sage.rings.polynomial.polynomial_element import Polynomial
from sage.rings.polynomial.polynomial_ring import PolynomialRing_general


FpElement: TypeAlias = RingElement
FprElement: TypeAlias = RingElement
FprPoly: TypeAlias = Polynomial #Polynomial with coeff in FPR

S: PolynomialRing_general
T: Polynomial

# from agents import Prover, Verifier

# ---------------------------------------------------
# Field Setup
# ---------------------------------------------------

p = 5
r = 3

Fp = GF(p)
Fpr = Fp.extension(r, 'a')
S, T = PolynomialRing(Fpr, 'T').objgen()


print(f"modulus of field is {Fpr.modulus()}")

# ---------------------------------------------------
# VOLE relation object
# ---------------------------------------------------



@dataclass
class RandomVOLE:
    u: FpElement
    b: FprElement
    v: FprElement
    d: FpElement

    def check(self, delta: RingElement) -> bool:
        return self.v == (delta * self.u) + self.b

@dataclass
class VOLEProver:
    rho_w_t: FprPoly

    def __str__(self) -> str:
        return f"(rho_w_t={self.rho_w_t})"
    


@dataclass
class VOLEVerifier:
    gamma_w_delta: FprElement

    def __str__(self) -> str:
        return f"(gamma_w_delta={self.gamma_w_delta})"


@dataclass
class VOLE:
    proverVOLE: VOLEProver
    verifierVOLE: VOLEVerifier

    def __str__(self) -> str:
        return (
            "VOLE(\n"
            f"  prover   = {self.proverVOLE}\n"
            f"  verifier = {self.verifierVOLE}\n"
            ")"
        )







@dataclass
class VOLETuple:
    degree :int

    #random vole
    rho_u_t:       FprPoly = None # uT + b
    gamma_u_delta: FprPoly = None #u(T=Delta)+b

    u: FpElement  | None = None #random vole
    b: FprElement | None = None
    v: FprElement | None = None # random vole evaluation
    

    # witness vole
    w: FpElement | None = None # prover's actual witness
    # w_poly: RingElement | None = None # polynomial representation of witness, used for opening phase
    q: FprElement | None = None #VOLE evaluation on the witness q = v + d Delta = u Delta + b + w Delta - u Delta = w delta + b
    rho_w_t: FprPoly | None = None # 
    gamma_w_delta: FprPoly | None = None

    # correction values
    correction_prover: FpElement | None = None # correction value d = w -u
    correction_verifier: FpElement | None = None # correction value d = w -u, stored on verifiers side after transmission from prover


    


    def check(self, delta: RingElement) -> bool:
        # check random vole is valid
        if self.u is None or self.b is None or self.v is None:
            return False
        return self.v == (delta * self.u) + self.b

    # def __str__(self):
    #     return (
    #         f"(u={self.u}, b={self.b}, v={self.v})"
    #         f"(w={self.w}, b={self.b}, q={self.q})"
    #         f"(P correction={self.correction_prover}, V correction={self.correction_verifier})"            
    #         )
    
    def __str__(self):
        return (
            f"({self.rho_w_t=})"
            f"({self.gamma_w_delta=})"                        
            )
    
    
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
    vole_tuples_prover: list[VOLEProver] = field(default_factory=list)
    

    def append_commit(self, u: FpElement, b: FpElement, rho_u_t: FprPoly, degree: int) -> None:
        # internal function to append a commit
        self.vole_tuples.append(VOLETuple(u=u, b=b, rho_u_t=rho_u_t, degree=degree))

    def __str__(self):
        tuples_str = "\n".join(str(t) for t in self.vole_tuples_prover)
        return (
            "=== Prover ===\n"
            # f"witness: {self.w}\n"
            f"VOLE tuples:\n{tuples_str}"
        )
    def update_witness(self, w:FpElement, index:int)->FprPoly:
        """ 
         Update ith witness 
        """
        self.vole_tuples[index].w = w
        rho_w_t = w*T + self.vole_tuples[index].b
        self.vole_tuples[index].rho_w_t = rho_w_t
        return rho_w_t

    def compute_correction_value_d(self, index:int)->None:
        # compute correction value
        w = self.vole_tuples[index].w
        u = self.vole_tuples[index].u
        d = w - u
        return d
    
    def update_correction_value(self, corrrection_value_d:FpElement, index:int)->None:
        """
        update correction avlue "d = w-u
        """
        self.vole_tuples[index].correction_prover = corrrection_value_d

    
        
        


@dataclass
class Verifier:
    delta: FprElement | None = None
    vole_tuples: list[VOLETuple] = field(default_factory=list)
    vole_tuples_verifier: list[VOLEVerifier] = field(default_factory=list)

    def append_eval(self, v:FprElement, gamma_u_delta:FprElement, degree:int)->None:
        self.vole_tuples.append(VOLETuple(u=None, b=None, v=v, gamma_u_delta=gamma_u_delta, degree=degree))

    def __str__(self):
        tuples_str = "\n".join(str(t) for t in self.vole_tuples_verifier)
        return (
            "=== Verifier ===\n"
            f"delta: {self.delta}\n"
            f"VOLE evaluations:\n{tuples_str}"
        )
    
    def update_correction(self, correction_value_d:FpElement, index:int)->None:
        """
        update correction avlue "d = w-u
        """
        self.vole_tuples[index].correction_verifier = correction_value_d

    
    def update_eval_with_correction(self,d:FpElement,index:int)->None:
        # adjust on verifiers side:
        v = self.vole_tuples[index].v # get v
        
        q = v + (self.delta * d) # adjust v with correction value d and delta to get 
        #q = v + d Delta = u Delta + b + w Delta - u Delta = w delta + b
        gamma_w_delta = self.vole_tuples[index].gamma_u_delta + (self.delta * d) # adjust gamma_u_delta with correction value d and delta to get gamma_w_delta = u Delta + b + w Delta - u Delta = w delta + b
        print(f"{gamma_w_delta=}")
        assert q == gamma_w_delta, "Adjusted evaluation does not match expected value"
        self.vole_tuples[index].q = q #update q in verifiers state
        self.vole_tuples[index].gamma_w_delta =gamma_w_delta # copy into poly
        return gamma_w_delta

# ---------------------------------------------------
# Testing
# ---------------------------------------------------

def test_evaluation(prover: Prover, verifier: Verifier):

    for i in range(len(prover.vole_tuples)):

        p_tuple = prover.vole_tuples[i]
        v_tuple = verifier.vole_tuples[i]

        vole_random = VOLETuple(u=p_tuple.u, b=p_tuple.b, v=v_tuple.v, degree=p_tuple.degree)
        vole_witness = VOLETuple(w=p_tuple.w, b=p_tuple.b, q=v_tuple.q , degree=p_tuple.degree)

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

        length = args[0]
        # generate l number of random, VOLES

        print(f"Generating {length} VOLE tuples")

        for _ in range(length):

            u = Fp.random_element() # sample u

            b = Fpr.random_element() # macro auth starts here

            
            #--------- rho_u(t) = u T + b (testing rn)------------------------
            
            rho_u_t = u * T + b
            

            # verifier evaluates rho_u at delta to get v
            gamma_u_delta = rho_u_t(verifier.delta) # this is the same as u*delta + b

            v = verifier.delta * u + b

            assert gamma_u_delta == v, "Evaluation of rho_u at delta does not match expected value"
            #-----------------------------------

            prover.append_commit(u, b, rho_u_t, degree=1)
            verifier.append_eval(v, gamma_u_delta, degree=1)

            #-----------------------------------
            
            #------------------------------------

            print(f"(u={u}, b={b}, v={v}) : {v}={u}*{verifier.delta}+{b} mod {p}")
    




def commit(prover:Prover, verifier: Verifier, witness: list[FpElement], degree:int)-> None:
    """
    Commit phase of sVOLE protocol.
    x in [Fp, Fp...] is the list of witnesses that the prover wants to commit to, and prove knowledge of.  
    1. Generate l number of random VOLE tuples, where l is the length of the witness list.
    2. For each witness, compute correction value d = w-u
    3. P stores correction, sends to V, V stores correction.
    4. V adjusts its VOLE evaluation with the correction value, to get q = v + d Delta = u Delta + b + w Delta - u Delta = w delta + b
    """

    length_witness = len(witness)
    #1. request l number of  degree 1 random VOLE tuples
    sVOLE(prover, verifier, "sVOLE", length_witness)

    # 2. compute correction value and send to V
    for i in range(length_witness):
        w = witness[i]
        # add witness to prover's state
        rho_w_t= prover.update_witness(w, i)

        # Prover computes correction value 
        d = prover.compute_correction_value_d(i)
        print(f"correction value is {d}")

        # store correction value in  provers state
        prover.update_correction_value(d, i)

        # simulate sending correction to verifer
        
        # 3. Adjust on V's side
        # verifier recieved d, stores d 
        verifier.update_correction(d,i)

        #verifier recomputes vole evaluation and updates it
        gamma_w_delta= verifier.update_eval_with_correction(d,i)

        #create PROVER and verifier voles
        proverVOLE = VOLEProver(
            rho_w_t=rho_w_t,
        )

        verifierVOLE = VOLEVerifier(
            gamma_w_delta=gamma_w_delta,
        )

        vole = VOLE(
            proverVOLE=proverVOLE,
            verifierVOLE=verifierVOLE
        )

        prover.vole_tuples_prover.append(proverVOLE)
        verifier.vole_tuples_verifier.append(verifierVOLE)




    
    

def open(prover: Prover, verifier: Verifier, index:int, degree:int , x:FpElement = None)->None:
    """
    Open phase of sVOLE protocol.
    Prover sends polynomial rho_w(t) i.e the coefficients, w
    V checks if :
    1. rho_w(t=Delta) = gamma_w_delta
    2. rho_w(t)[highest degree co-eff] = w    
    3. degree(rho_w(t)) == d 
    """
    if x is None:
        x = prover.vole_tuples[index].w 
    #--sanity checks---
    assert index < len(prover.vole_tuples), "Invalid index for opening"
    assert index < len(verifier.vole_tuples), "Invalid index for opening"
    assert prover.vole_tuples[index].w == x, f"Prover's witness: {prover.vole_tuples[index].w}, expected witness: {x}"
    #----

    rho_w_t = prover.vole_tuples[index].rho_w_t #prover sends this and all associatyed data such as degree
    assert rho_w_t(verifier.delta) == verifier.vole_tuples[index].gamma_w_delta, "eval not equal"
    
    if rho_w_t.degree() != rho_w_t.degree :
        print(f"degree of rho_w_t is {rho_w_t.degree()}, expected degree is {rho_w_t.degree}")
        # wrapped around and highest degree term in 0

    assert rho_w_t.coefficients()[-1]== x, "highest degree coefficeint not equal"
    
    # assert 
    # add degree check

    print(f"opening of {x=} succesful")
    pass


def VOLE_add(prover:Prover, verifier:Verifier, x_index:int, y_index:int):
    
    p1 = prover.vole_tuples[x_index].rho_w_t
    p1_verifier = verifier.vole_tuples[x_index].gamma_w_delta
    p2 = prover.vole_tuples[y_index].rho_w_t
    p2_verifier = verifier.vole_tuples[y_index].gamma_w_delta
    d1 = p1.degree()
    d2 = p2.degree()
    print(f"d1={d1}, d2={d2}")
    Delta = verifier.delta

    if d1==d2:
        
        p3 = p1 + p2        
        
        p3_verifier = p1_verifier + p2_verifier
        degree = d1
        # print(f"{p3=}")
        
        # print(f"p3_verifier={p3_verifier}")
        
    elif d2>d1:
        degree = d2
        p3 = p1* T**(d2-d1) + p2
        p3_verifier = p1_verifier* Delta**(d2-d1) + p2_verifier
        # print(f"{p3=}")
        # print(f"p3_verifier={p3_verifier}")

    elif d1>d2:
        degree = d1
        p3 = p2* T**(d1-d2) + p1
        p3_verifier = p2_verifier* Delta**(d1-d2) + p1_verifier
        # print(f"{p3=}")
        # print(f"p3_verifier={p3_verifier}")

    print(f"degree of p3 is {p3.degree()}, expected degree is {degree}")
    if degree != p3.degree():
        # wrapped around and highest degree term in 0 
        w = 0
    else:
        w = p3.coefficients()[-1]
    
    # add VOLE tuple to prover and verifier state
    prover.vole_tuples.append(VOLETuple(degree=degree, rho_w_t=p3, w = w))
    verifier.vole_tuples.append(VOLETuple(degree=degree, gamma_w_delta=p3_verifier))




# ---------------------------------------------------
# Run protocol
# ---------------------------------------------------

prover = Prover()
verifier = Verifier()

sVOLE(prover, verifier, "Init")

VOLES_global_list = []

VOLES_user_defined = [Fp(1), Fp(4)]

commit(prover, verifier, VOLES_user_defined, 1)


# sVOLE(prover, verifier, "sVOLE", 1)


VOLE_add(prover, verifier, 0, 1)


print()
print(prover)
print()
print(verifier)

# test_evaluation(prover, verifier)

open(prover, verifier, 0, 1,  VOLES_user_defined[0])
open(prover, verifier, 1, 1, VOLES_user_defined[1])
open(prover, verifier, 2, 1)



