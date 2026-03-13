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

p = 2**31 -1
r = 4

Fp = GF(p)
Fpr = Fp.extension(r, 'a')
S, T = PolynomialRing(Fpr, 'T').objgen()


print(f"modulus of field is {Fpr.modulus()}")

# ---------------------------------------------------
# VOLE relation object
# ---------------------------------------------------





@dataclass
class VOLETuple:
    context: str #context in terms of witness
    degree_poly :int #need ot keep track of the degree as sage consideres 0T^3 + 6T^2 + 2 to have degree 2, not 3 which casues problems with addition and keeping track of witness

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
            f"({self.context=})"      
            f"({self.w})"                  
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
    vole_tuples: list[VOLETuple] = field(default_factory=list)

    
    
    

    def append_random_commit(self, u: FpElement, b: FpElement, rho_u_t: FprPoly, degree_poly: int, context: str) -> None:
        # internal function to append a commit
        # if commit = random

        # if commti = from function


        self.vole_tuples.append(VOLETuple(u=u, b=b, rho_u_t=rho_u_t, degree_poly=degree_poly, context=context))

    def __str__(self):
        tuples_str = "\n".join(str(t) for t in self.vole_tuples)
        return (
            "=== Prover ===\n"
            # f"witness: {self.w}\n"
            f"VOLE tuples:\n{tuples_str}"
        )
    def update_random_commit_with_witness(self, w:FpElement, index:int)->tuple[FprPoly, FpElement]:
        """prover now sends a witness, this function 
        1. adds witness to prover's VOLE Tuple state
        2. Computes the provers polynomail
        3. Computes correction value d-u and adds it to state by calling compute_correction_value_d


        Args:
            w (FpElement): Prover's witness that it wants to commit to
            index (int): Index of the random VOLE that it wants to overwrite

        Returns:
            tuple[FprPoly, FpElement]: Prover's polynomail, correction value d = w - u
        """


        
       
        self.vole_tuples[index].context = f"w_{index}={w}"
        self.vole_tuples[index].w = w
        rho_w_t = w*T + self.vole_tuples[index].b # compute prover polynomail
        self.vole_tuples[index].rho_w_t = rho_w_t # update prover polynomial

        d = self.compute_correction_value_d(index)


        return (rho_w_t, d)

    def compute_correction_value_d(self, index:int)->FpElement:
        """ Computes the correction value d = w-u, and adds d to prover state
        This is called by prover.update_random-commit_with_witness

        Args:
            index (int): index of the VOLE tuple to compute correction value of

        Returns:
            (FpElement): correction value d = w-u
        """
        # compute correction value
        w = self.vole_tuples[index].w
        u = self.vole_tuples[index].u
        assert w is not None and u is not None, f"witness or random u not set for index {index}"
        d = w - u
        self.vole_tuples[index].correction_prover = d
        return d
    
   
    
        
        


@dataclass
class Verifier:
    delta: FprElement | None = None
    vole_tuples: list[VOLETuple] = field(default_factory=list)
    
    

    def append_random_eval(self, v:FprElement, gamma_u_delta:FprElement, degree_poly:int)->None:
        self.vole_tuples.append(VOLETuple(u=None, b=None, v=v, gamma_u_delta=gamma_u_delta, degree_poly=degree_poly, context= "None"))

    def __str__(self):
        tuples_str = "\n".join(str(t) for t in self.vole_tuples)
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
    #not in use

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

            prover.append_random_commit(u, b, rho_u_t, degree_poly=1, context="random_vole")
            verifier.append_random_eval(v, gamma_u_delta, degree_poly=1)

            #-----------------------------------
            
            #------------------------------------

            print(f"(u={u}, b={b}, v={v}) : {v}={u}*{verifier.delta}+{b} mod {p}")
    




def commit(prover:Prover, verifier: Verifier, witness: list[FpElement], degree_poly:int)-> None:
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
        # compute a valid VOLE on witness, and get the correction value
        (rho_w_t,d)= prover.update_random_commit_with_witness(w, i)        
        print(f"correction value is {d}")


        # simulate sending correction to verifer
        
        # 3. Adjust on V's side
        # verifier recieved d, stores d 
        verifier.update_correction(d,i)

        #verifier recomputes vole evaluation and updates it
        gamma_w_delta= verifier.update_eval_with_correction(d,i)



    

def open(prover: Prover, verifier: Verifier, index:int,  x:FpElement = None)->None:
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
    assert prover.vole_tuples[index].w == x, f"Prover's witness: {prover.vole_tuples[index].w}, you gave me: {x}"
    #----

    rho_w_t = prover.vole_tuples[index].rho_w_t #prover sends this and all associatyed data such as degree
    assert rho_w_t is not None, "Prover's VOLE polynomial is None"
    assert rho_w_t(verifier.delta) == verifier.vole_tuples[index].gamma_w_delta, "eval not equal"
    

    print(f"At {index=} opening of {x=} succesful")
    pass


def VOLE_add(prover:Prover, verifier:Verifier, x_index:int, y_index:int)->int:
    """Adds to VOLES 
    Add: [[x + y]]^p_d = [[x]]^p_d1 + [[y]]^p_d2 , where d = d2 and d1 ≤ d2:  
    • P outputs ρ_z(t) = t^(d2-d1) ρ_x(t) + ρ_y(t)  
    • V outputs γ_z = Δ^(d_2−d_1) γ_x + γ_y

    This function:
    1. Adds 2 voles and stores the output in both prover and verifier state.(we sanity check they are equal)
    2. computes the degree of the resultant vole and stores that in prover's state(need to add verifier state storing)
    3. computes the witness of the resultant vole and adds that (ie t he highest degree coeff)
    4. computes context string f.ex w3=w1+w2 and adds that to provers vole tuple

    Args:
        prover (Prover): _description_
        verifier (Verifier): _description_
        x_index (int): index of the 1st addend VOLE typle at prover/verifier
        y_index (int): index of the 2nd addend vole tuple at the prover and the verrifier

    Returns:
        int: index of the resultant vole in provers state
    """
    
    p1 = prover.vole_tuples[x_index].rho_w_t
    p1_verifier = verifier.vole_tuples[x_index].gamma_w_delta
    p2 = prover.vole_tuples[y_index].rho_w_t
    p2_verifier = verifier.vole_tuples[y_index].gamma_w_delta

    assert p1 is not None, f"Prover's VOLE polynomial is None for index {x_index}"
    assert p2 is not None, f"Prover's VOLE polynomial is None for index {y_index}"
    assert p1_verifier is not None, f"Verifier's VOLE evaluation is None for index {x_index}"
    assert p2_verifier is not None, f"Verifier's VOLE evaluation is None for index {y_index}"

    d1 = p1.degree()
    d2 = p2.degree()
    print(f"d1={d1}, d2={d2}")
    Delta = verifier.delta

    
    

    
    if d1==d2:     
        
        p3 = p1 + p2        
        
        p3_verifier = p1_verifier + p2_verifier
        degree_poly = d1

        # add witness
        
        # print(f"p3_verifier={p3_verifier}")
        
    elif d2>d1:
        degree_poly = d2
        p3 = p1* T**(d2-d1) + p2
        p3_verifier = p1_verifier* Delta**(d2-d1) + p2_verifier
        # print(f"{p3=}")
        # print(f"p3_verifier={p3_verifier}")

    else: # d1>d2:
        degree_poly = d1
        p3 = p2* T**(d1-d2) + p1
        p3_verifier = p2_verifier* Delta**(d1-d2) + p1_verifier
        # print(f"{p3=}")
        # print(f"p3_verifier={p3_verifier}")

    

    # Possibility 1: if degree_poly == p3.degree(), then highest coeff is witness
    # we do this becuase if p3's higehst coeff is 0,  sage does not actually store at, and reudces the degree internally i.e sage stores
    # polynoimials in norrmalized form, (leading 0 co-effs are automatically removed)
    print(f"degree of resulting polynomial is {p3.degree()}, expected degree is {degree_poly}")
    if degree_poly == p3.degree():
        p3_witness = p3.coefficients()[-1]
        print(f"witness is {p3_witness}")
    else : 
        #p3.degree()< degree_poly:
        assert p3.degree() < degree_poly, f"Degree of resulting polynomial {p3.degree()} according to sage is less than expected {degree_poly}"
    # Possibility 2: if degree_poly < p3.degree(), then we might have wrapped and gotten 0 as highest coeff, then witness is 0
        p3_witness = 0
        print(f"degree of resulting polynomial is less than expected, possible wrap around, setting witness to 0")
    
    context = f"{prover.vole_tuples[x_index].context} + {prover.vole_tuples[y_index].context}"
    # add VOLE tuple to prover and verifier state
    
    prover.vole_tuples.append(VOLETuple(degree_poly=degree_poly, rho_w_t=p3, w = p3_witness, context = context))
    verifier.vole_tuples.append(VOLETuple(degree_poly=degree_poly, gamma_w_delta=p3_verifier, context="None"))

    p3_index = len(prover.vole_tuples) -1
    return p3_index

def VOLE_add_constant(prover:Prover, verifier:Verifier, x_index:int, y:FpElement)->int:    
    p1 = prover.vole_tuples[x_index].rho_w_t
    p1_verifier = verifier.vole_tuples[x_index].gamma_w_delta
    Delta = verifier.delta
    
    assert p1 is not None, f"Prover's VOLE polynomial is None for index {x_index}"
    assert p1_verifier is not None, f"Verifier's VOLE evaluation is None for index {x_index}"
    assert Delta is not None, f"Verifier's Delta is None"


    d1 = p1.degree()
    p1_degree_from_state = prover.vole_tuples[x_index].degree_poly
    assert p1_degree_from_state is not None, f"Prover's VOLE poly's degree is none for index {x_index}"

    

    print(f"d1={d1}, {p1_degree_from_state=}")
    if d1 == p1_degree_from_state:
        print(f"degree from state matches degree from sage, using degree from state")
        p3_witness = p1.coefficients()[-1] + y
    else: 
        print(f"degree from state is greater than degree from sage, possible wrap around, using degree from state and setting witness to {y}")
        p3_witness = y

    degree_poly = max(p1_degree_from_state, d1)
    assert degree_poly is not None 
    print(f"{degree_poly=}")
  
    p2 = Fp(y) * T**degree_poly
    p3 = p1 + p2

    p3_verifier = p1_verifier + (Delta**degree_poly * Fp(y))
    
    print(f"{p3=}")
    print(f"{p3_verifier=}")

    assert p3(Delta)== p3_verifier, f"prover and verifier vole matches" # sanity check

        
    context = f"{prover.vole_tuples[x_index].context} + {y}"
    # add VOLE tuple to prover and verifier state
    
    prover.vole_tuples.append(VOLETuple(degree_poly=degree_poly, rho_w_t=p3, w = p3_witness, context = context))
    verifier.vole_tuples.append(VOLETuple(degree_poly=degree_poly, gamma_w_delta=p3_verifier, context="None"))


    p3_index = len(prover.vole_tuples) -1
    print(f"redult added at index {p3_index=}")
    return p3_index


def VOLE_multiply(prover:Prover, verifier:Verifier, x_index:int, y_index:int)->int:
    p1 = prover.vole_tuples[x_index].rho_w_t
    p1_verifier = verifier.vole_tuples[x_index].gamma_w_delta
    p2 = prover.vole_tuples[y_index].rho_w_t
    p2_verifier = verifier.vole_tuples[y_index].gamma_w_delta

    assert p1 is not None, f"Prover's VOLE polynomial is None for index {x_index}"
    assert p2 is not None, f"Prover's VOLE polynomial is None for index {y_index}"
    assert p1_verifier is not None, f"Verifier's VOLE evaluation is None for index {x_index}"
    assert p2_verifier is not None, f"Verifier's VOLE evaluation is None for index {y_index}"

    d1_poly = prover.vole_tuples[x_index].degree_poly
    d2_poly = prover.vole_tuples[y_index].degree_poly
    
    Delta = verifier.delta


    
    print(f"{Delta=}")
    

    p3 = p1*p2
    p3_verifier = p1_verifier * p2_verifier
    print(f"{p3=}")
    print(f"{p3_verifier=}")
    assert p3(Delta)==p3_verifier, f"mult does not match up"

    degree_poly = d1_poly + d2_poly
    if degree_poly == p1.degree() + p2.degree():
        #witness is the highest coeff in p3
        p3_witness =p3.coefficients()[-1]
    else:
        #p1.degree()+p2.degree()<degree_poly
        p3_witness=0

    

    context = f"({prover.vole_tuples[x_index].context}) * ({prover.vole_tuples[y_index].context})"
    # add VOLE tuple to prover and verifier state
    
    prover.vole_tuples.append(VOLETuple(degree_poly=degree_poly, rho_w_t=p3, w = p3_witness, context = context))
    verifier.vole_tuples.append(VOLETuple(degree_poly=degree_poly, gamma_w_delta=p3_verifier, context="None"))

    p3_index = len(prover.vole_tuples) -1
    return p3_index



# ---------------------------------------------------
# Run protocol
# ---------------------------------------------------

prover = Prover()
verifier = Verifier()

sVOLE(prover, verifier, "Init")



witness = [Fp(1), Fp(3)]
voles_list = []

id0_1 = commit(prover, verifier, witness, 1)


# sVOLE(prover, verifier, "sVOLE", 1)


id_2= VOLE_add(prover, verifier, 0, 1)
id_3= VOLE_add(prover, verifier, 1, 2)
id_4=VOLE_add_constant(prover, verifier, 0, 3)
id_5= VOLE_multiply(prover, verifier, 0,1) #stored in 5
id_6=VOLE_multiply(prover, verifier, 2 ,  5) 


print()
print(prover)
print()
print(verifier)

# test_evaluation(prover, verifier)

open(prover, verifier, 0,  witness[0])
open(prover, verifier, 1,  witness[1])
open(prover, verifier, 2, witness[0]+witness[1])
open(prover, verifier, 3, )
open(prover, verifier, 4 )
open(prover, verifier, 5)
open(prover, verifier, 6)

#to dos:
# consider using leadingcoefficient for sage,p.leading_coefficient()
# add docstr9ings fro VOLE absed operations
# tests for VOLE based operations