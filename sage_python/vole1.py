from dataclasses import dataclass, field
from sage.all import *
from sage.structure.element import RingElement

# ---------------------------------------------------
# Field Setup
# ---------------------------------------------------

p = 5
r = 3

Fp = GF(p)
Fpr = Fp.extension(r, 'a')

print(f"modulus of field is {Fpr.modulus()}")

# ---------------------------------------------------
# VOLE relation object
# ---------------------------------------------------

@dataclass
class VOLETuple:
    u: RingElement
    b: RingElement
    v: RingElement | None = None

    def check(self, delta: RingElement) -> bool:
        return self.v == delta * self.u + self.b

    def __str__(self):
        return f"(u={self.u}, b={self.b}, v={self.v})"


# ---------------------------------------------------
# Prover / Verifier State
# ---------------------------------------------------

@dataclass
class Prover:
    w: list[RingElement] | None = None
    vole_tuples: list[VOLETuple] = field(default_factory=list)

    def add_commit(self, u, b):
        self.vole_tuples.append(VOLETuple(u=u, b=b))

    def __str__(self):
        tuples_str = "\n".join(str(t) for t in self.vole_tuples)
        return (
            "=== Prover ===\n"
            f"witness: {self.w}\n"
            f"VOLE tuples:\n{tuples_str}"
        )


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


# ---------------------------------------------------
# Testing
# ---------------------------------------------------

def test_evaluation(prover: Prover, verifier: Verifier):

    for i in range(len(prover.vole_tuples)):

        p_tuple = prover.vole_tuples[i]
        v_tuple = verifier.vole_tuples[i]

        vole = VOLETuple(u=p_tuple.u, b=p_tuple.b, v=v_tuple.v)

        assert vole.check(verifier.delta),"Evaluation failed"

    print("All VOLE relations verified ✓")


# ---------------------------------------------------
# sVOLE protocol
# ---------------------------------------------------

def sVOLE(prover: Prover, verifier: Verifier, command, *args):

    if command == "Init":

        delta = Fpr.random_element()
        verifier.delta = delta

        print(f"Verifier sampled Δ = {delta}")

    elif command == "sVOLE":

        l = args[0]

        print(f"Generating {l} VOLE tuples")

        for _ in range(l):

            u = Fp.random_element()
            b = Fpr.random_element()

            v = verifier.delta * u + b

            prover.add_commit(u, b)
            verifier.add_eval(v)

            print(f"(u={u}, b={b}, v={v})")


# ---------------------------------------------------
# Run protocol
# ---------------------------------------------------

prover = Prover()
verifier = Verifier()

sVOLE(prover, verifier, "Init")
sVOLE(prover, verifier, "sVOLE", 3)

print()
print(prover)
print()
print(verifier)

test_evaluation(prover, verifier)