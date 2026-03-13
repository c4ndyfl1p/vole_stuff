import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from random import randint

from vole1 import *

def check_vole_relation(prover: Prover, verifier: Verifier, index: int):
    """Check rho_w(Delta) == gamma_w_delta"""
    rho = prover.vole_tuples[index].rho_w_t
    gamma = verifier.vole_tuples[index].gamma_w_delta
    Delta = verifier.delta

    assert rho is not None
    assert gamma is not None
    assert Delta is not None

    assert rho(Delta) == gamma, f"VOLE relation broken at index {index}"

def test_vole_add_basic_no_wrap_around():
    prover = Prover()
    verifier = Verifier()

    sVOLE(prover, verifier, "Init")

    witness = [Fp(2), Fp(1)]

    commit(prover, verifier, witness, 1)

    z_index = VOLE_add(prover, verifier, 0, 1)

    check_vole_relation(prover, verifier, z_index)

    expected = witness[0] + witness[1]

    assert prover.vole_tuples[z_index].w == expected
    assert prover.vole_tuples[z_index].degree_poly == 1


def test_vole_add_basic_wrap_around():
    prover = Prover()
    verifier = Verifier()

    sVOLE(prover, verifier, "Init")

    witness = [Fp(2), Fp(3)]

    commit(prover, verifier, witness, 1)

    z_index = VOLE_add(prover, verifier, 0, 1)

    check_vole_relation(prover, verifier, z_index)

    expected = witness[0] + witness[1]

    assert prover.vole_tuples[z_index].w == expected
    assert prover.vole_tuples[z_index].degree_poly == 1


def test_vole_add_degree_alignment():
    prover = Prover()
    verifier = Verifier()

    sVOLE(prover, verifier, "Init")

    witness = [Fp(1), Fp(4)]

    commit(prover, verifier, witness, 1)

    z_index = VOLE_add(prover, verifier, 0, 1)

    check_vole_relation(prover, verifier, z_index)

    p = prover.vole_tuples[z_index].rho_w_t
    assert p.degree() <= prover.vole_tuples[z_index].degree_poly

def test_random_voles_degrree():

    for _ in range(20):

        prover = Prover()
        verifier = Verifier()

        sVOLE(prover, verifier, "Init")

        w1 = Fp.random_element()
        w2 = Fp.random_element()

        commit(prover, verifier, [w1, w2], 1)

        z = VOLE_add(prover, verifier, 0, 1)

        check_vole_relation(prover, verifier, z)

def test_add_different_degrees():

    for _ in range(20):

        prover = Prover()
        verifier = Verifier()

        sVOLE(prover, verifier, "Init")

        Delta = verifier.delta

        # random degrees
        d1 = randint(1, 10)
        d2 = randint(1, 10)

        print(f"test_add_different_degrees: {d1=} {d2=}")

        # random coefficients
        y1 = Fp.random_element()
        y2 = Fp.random_element()
        

        # create polynomials
        p1 = y1 * T**d1 + Fpr.random_element()
        p2 = y2 * T**d2 + Fpr.random_element()
        print(f"test_add_different_degrees: {p1=} {p2=}")

        gamma1 = p1(Delta)
        gamma2 = p2(Delta)

        prover.vole_tuples.append(
            VOLETuple(degree_poly=d1, rho_w_t=p1, w=y1, context="test1")
        )

        verifier.vole_tuples.append(
            VOLETuple(degree_poly=d1, gamma_w_delta=gamma1, context="test1")
        )

        prover.vole_tuples.append(
            VOLETuple(degree_poly=d2, rho_w_t=p2, w=y2, context="test2")
        )

        verifier.vole_tuples.append(
            VOLETuple(degree_poly=d2, gamma_w_delta=gamma2, context="test2")
        )

        z = VOLE_add(prover, verifier, 0, 1)

        check_vole_relation(prover, verifier, z) # check relation;s provers poly, verifeirs polky and delta matches up
        

        p3 = prover.vole_tuples[z].rho_w_t

        
def test_add_dense_random_polynomials():

    for _ in range(20):

        prover = Prover()
        verifier = Verifier()

        sVOLE(prover, verifier, "Init")

        Delta = verifier.delta

        # random degrees
        d1 = randint(1, 10)
        d2 = randint(1, 10)

        print(f"test_add_dense_random_polynomials: {d1=} {d2=}")

        # ensure leading coefficient not zero
        y1 = Fpr.random_element()
        while y1 == 0:
            y1 = Fpr.random_element()

        y2 = Fpr.random_element()
        while y2 == 0:
            y2 = Fpr.random_element()

        # create dense polynomials
        coeffs1 = [Fpr.random_element() for _ in range(d1)]
        coeffs1.append(y1)

        coeffs2 = [Fpr.random_element() for _ in range(d2)]
        coeffs2.append(y2)

        p1 = S(coeffs1)
        p2 = S(coeffs2)

        print(f"test_add_dense_random_polynomials: {p1=} {p2=}")

        gamma1 = p1(Delta)
        gamma2 = p2(Delta)

        prover.vole_tuples.append(
            VOLETuple(degree_poly=d1, rho_w_t=p1, w=y1, context="dense_test1")
        )

        verifier.vole_tuples.append(
            VOLETuple(degree_poly=d1, gamma_w_delta=gamma1, context="dense_test1")
        )

        prover.vole_tuples.append(
            VOLETuple(degree_poly=d2, rho_w_t=p2, w=y2, context="dense_test2")
        )

        verifier.vole_tuples.append(
            VOLETuple(degree_poly=d2, gamma_w_delta=gamma2, context="dense_test2")
        )

        z = VOLE_add(prover, verifier, 0, 1)

        check_vole_relation(prover, verifier, z)

        p3 = prover.vole_tuples[z].rho_w_t

        # expected polynomial according to protocol
        if d1 <= d2:
            expected = p1 * T**(d2 - d1) + p2
        else:
            expected = p2 * T**(d1 - d2) + p1

        assert p3 == expected