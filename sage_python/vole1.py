from sage.all import *

p = 17

Fp = GF(p)        # finite field F_p
R, t = PolynomialRing(Fp, 't').objgen()    # polynomial ring F_p[t]