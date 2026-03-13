import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from random import randint

from vole1 import *

def check_vole_relation(prover, verifier, index):
    rho = prover.vole_tuples[index].rho_w_t
    gamma = verifier.vole_tuples[index].gamma_w_delta
    Delta = verifier.delta

    assert rho is not None
    assert gamma is not None
    assert Delta is not None

    assert rho(Delta) == gamma

def test_add_constant_basic():

    prover = Prover()
    verifier = Verifier()

    sVOLE(prover, verifier, "Init")

    Delta = verifier.delta

    w = Fp.random_element()
    commit(prover, verifier, [w], 1)

    y = Fp.random_element()

    z = VOLE_add_constant(prover, verifier, 0, y)

    check_vole_relation(prover, verifier, z)

    p1 = prover.vole_tuples[0].rho_w_t
    p3 = prover.vole_tuples[z].rho_w_t

    d = prover.vole_tuples[z].degree_poly

    expected = p1 + y * T**d

    assert p3 == expected

def test_add_constant_random_degrees():

    for _ in range(20):

        prover = Prover()
        verifier = Verifier()

        sVOLE(prover, verifier, "Init")

        Delta = verifier.delta

        d = randint(1,10)

        y1 = Fpr.random_element()
        while y1 == 0:
            y1 = Fpr.random_element()

        coeffs = [Fpr.random_element() for _ in range(d)]
        coeffs.append(y1)

        p1 = S(coeffs)

        gamma1 = p1(Delta)

        prover.vole_tuples.append(
            VOLETuple(degree_poly=d, rho_w_t=p1, w=y1, context="test")
        )

        verifier.vole_tuples.append(
            VOLETuple(degree_poly=d, gamma_w_delta=gamma1, context="test")
        )

        y = Fp.random_element()

        z = VOLE_add_constant(prover, verifier, 0, y)

        check_vole_relation(prover, verifier, z)

        p3 = prover.vole_tuples[z].rho_w_t

        expected = p1 + y*T**d

        assert p3 == expected

def test_add_constant_random():

    for _ in range(50):

        prover = Prover()
        verifier = Verifier()

        sVOLE(prover, verifier, "Init")

        w = Fp.random_element()

        commit(prover, verifier, [w], 1)

        y = Fp.random_element()

        z = VOLE_add_constant(prover, verifier, 0, y)

        check_vole_relation(prover, verifier, z)