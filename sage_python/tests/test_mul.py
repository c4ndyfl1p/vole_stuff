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

def test_multiply_basic():

    prover = Prover()
    verifier = Verifier()

    sVOLE(prover, verifier, "Init")

    w1 = Fp(2)
    w2 = Fp(3)

    commit(prover, verifier, [w1, w2], 1)

    z = VOLE_multiply(prover, verifier, 0, 1)

    check_vole_relation(prover, verifier, z)

    expected_witness = w1 * w2

    assert prover.vole_tuples[z].w == expected_witness
