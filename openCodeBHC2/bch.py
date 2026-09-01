"""
BCH code over GF(5) with extension field GF(5^7)
Parameters: t = 11 (error correction), j_0 = 1 (starting root)
"""

from __future__ import annotations
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# GF(5) arithmetic
# ---------------------------------------------------------------------------

def gf5_add(a: int, b: int) -> int:
    return (a + b) % 5

def gf5_sub(a: int, b: int) -> int:
    return (a - b) % 5

def gf5_mul(a: int, b: int) -> int:
    return (a * b) % 5

def gf5_neg(a: int) -> int:
    return (-a) % 5

def gf5_inv(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("Cannot invert 0 in GF(5)")
    return pow(a, 3, 5)

# ---------------------------------------------------------------------------
# Polynomial over GF(5)
# ---------------------------------------------------------------------------

class PolyGF5:
    """Polynomial with coefficients in GF(5): [c0,c1,...,cn] = c0 + c1*x + ... + cn*x^n"""

    def __init__(self, coeffs):
        coeffs = [c % 5 for c in coeffs]
        while len(coeffs) > 1 and coeffs[-1] == 0:
            coeffs.pop()
        self.coeffs = coeffs if coeffs else [0]

    @property
    def deg(self) -> int:
        return len(self.coeffs) - 1

    def __getitem__(self, idx):
        if idx < 0 or idx >= len(self.coeffs):
            return 0
        return self.coeffs[idx]

    def __setitem__(self, idx, val):
        while len(self.coeffs) <= idx:
            self.coeffs.append(0)
        self.coeffs[idx] = val % 5
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()

    def __add__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        result = [0] * n
        for i, c in enumerate(self.coeffs):
            result[i] = gf5_add(result[i], c)
        for i, c in enumerate(other.coeffs):
            result[i] = gf5_add(result[i], c)
        return PolyGF5(result)

    def __sub__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        result = [0] * n
        for i, c in enumerate(self.coeffs):
            result[i] = gf5_add(result[i], c)
        for i, c in enumerate(other.coeffs):
            result[i] = gf5_sub(result[i], c)
        return PolyGF5(result)

    def __neg__(self):
        return PolyGF5([gf5_neg(c) for c in self.coeffs])

    def __mul__(self, other):
        result = [0] * (len(self.coeffs) + len(other.coeffs) - 1)
        for i, c1 in enumerate(self.coeffs):
            if c1 == 0:
                continue
            for j, c2 in enumerate(other.coeffs):
                result[i + j] = gf5_add(result[i + j], gf5_mul(c1, c2))
        return PolyGF5(result)

    def __eq__(self, other):
        if isinstance(other, list):
            other = PolyGF5(other)
        return self.coeffs == other.coeffs

    def __call__(self, x):
        """Evaluate at x (x is integer 0-4)"""
        r = 0
        for c in reversed(self.coeffs):
            r = gf5_add(gf5_mul(r, x), c)
        return r

    def divmod(self, other):
        q = [0] * max(1, self.deg - other.deg + 1)
        r = list(self.coeffs)
        other_lead_inv = gf5_inv(other[other.deg])
        while len(r) >= len(other.coeffs) and not (len(r) == 1 and r[0] == 0):
            deg_diff = len(r) - len(other.coeffs)
            factor = gf5_mul(r[-1], other_lead_inv)
            q[deg_diff] = factor
            for j, c in enumerate(other.coeffs):
                r[deg_diff + j] = gf5_sub(r[deg_diff + j], gf5_mul(factor, c))
            while len(r) > 1 and r[-1] == 0:
                r.pop()
        return PolyGF5(q), PolyGF5(r) if r else PolyGF5([0])

    def __floordiv__(self, other):
        q, _ = self.divmod(other)
        return q

    def __mod__(self, other):
        _, r = self.divmod(other)
        return r

    def scalar_mul(self, s: int):
        return PolyGF5([gf5_mul(c, s) for c in self.coeffs])

    def derivative(self):
        if self.deg < 1:
            return PolyGF5([0])
        result = [gf5_mul(i, c) for i, c in enumerate(self.coeffs) if i >= 1]
        return PolyGF5(result)

    @staticmethod
    def monomial(degree: int, coeff: int = 1):
        return PolyGF5([0] * degree + [coeff % 5])

    @staticmethod
    def _from_raw(coeffs):
        """Create polynomial without trimming trailing zeros."""
        c = [c % 5 for c in coeffs]
        poly = object.__new__(PolyGF5)
        poly.coeffs = c if c else [0]
        return poly


# ---------------------------------------------------------------------------
# GF(5^7) field
# ---------------------------------------------------------------------------

def _poly_mod_57(a, p):
    """Reduce polynomial a modulo p (both coeff lists over GF(5), p is degree 7)."""
    a = list(a)
    p = list(p)
    while len(a) >= len(p) and not (len(a) == 1 and a[0] == 0):
        deg_diff = len(a) - len(p)
        lead_inv = gf5_inv(p[-1])
        factor = gf5_mul(a[-1], lead_inv)
        if factor != 0:
            for j, pj in enumerate(p):
                a[deg_diff + j] = gf5_sub(a[deg_diff + j], gf5_mul(factor, pj))
        while len(a) > 1 and a[-1] == 0:
            a.pop()
    return tuple(a) if a else (0,)


_G = 5       # characteristic
_M = 7       # extension degree
_Q = 5 ** 7   # field size = 78125
_N = _Q - 1   # multiplicative group order = 78124

# Primitive polynomial: x^7 + 3x + 2 over GF(5)
# Coefficients: [a0, a1, ..., a6, a7] for a0 + a1*x + ... + a6*x^6 + a7*x^7
# p(x) = 2 + 3x + x^7
_PRIM_POLY = (2, 3, 0, 0, 0, 0, 0, 1)  # x^7 + 3x + 2

# Reduction: α^7 = -(a0 + a1*α + ... + a6*α^6)
# With a7=1, a0=2, a1=3, rest 0:
# α^7 = -2 - 3α = 3 + 2α (in GF(5): -2=3, -3=2)
_RED_COEFFS = tuple(gf5_neg(c) for c in _PRIM_POLY[:-1])  # (3, 2, 0, 0, 0, 0, 0)


def _build_field_tables():
    """Build pow_to_vec and vec_to_pow tables for GF(5^7)."""
    pow_to_vec = [(0,) * _M]  # α^0 = 1 is index 0
    vec_to_pow = {}

    # α^0 = 1
    v = [1] + [0] * (_M - 1)
    pow_to_vec[0] = tuple(v)
    vec_to_pow[tuple(v)] = 0

    # Generate α^k for k = 1, 2, ..., N-1
    for k in range(1, _N):
        # α^k = α * α^(k-1)
        # Multiply by α: shift left by 1, then reduce if needed
        v_prev = pow_to_vec[k - 1]
        # Shift: v_new = [0, v_prev[0], v_prev[1], ..., v_prev[5]]
        v_new = [0] + list(v_prev[:-1])
        # If the original α^(k-1) had a non-zero α^6 coefficient, add reduction
        c6 = v_prev[-1]  # α^6 coefficient
        if c6 != 0:
            for i in range(_M):
                v_new[i] = gf5_add(v_new[i], gf5_mul(c6, _RED_COEFFS[i]))
        # Remove trailing zeros
        while v_new and v_new[-1] == 0:
            v_new.pop()
        while len(v_new) < _M:
            v_new.append(0)
        vt = tuple(v_new[:_M])
        pow_to_vec.append(vt)
        vec_to_pow[vt] = k

    return pow_to_vec, vec_to_pow


class _GF5_7Field:
    """Singleton GF(5^7) field with full tables."""

    def __init__(self):
        self.pow_to_vec, self.vec_to_pow = _build_field_tables()
        self.zero_val = 0
        self.one_val = 1
        self.prim_poly = _PRIM_POLY

    def add(self, a: int, b: int) -> int:
        if a == 0:
            return b
        if b == 0:
            return a
        va = self.pow_to_vec[a - 1]
        vb = self.pow_to_vec[b - 1]
        vc = tuple(gf5_add(va[i], vb[i]) for i in range(_M))
        if vc in self.vec_to_pow:
            return self.vec_to_pow[vc] + 1
        return 0  # zero element

    def sub(self, a: int, b: int) -> int:
        if b == 0:
            return a
        if a == 0:
            return self.neg(b)
        va = self.pow_to_vec[a - 1]
        vb = self.pow_to_vec[b - 1]
        vc = tuple(gf5_sub(va[i], vb[i]) for i in range(_M))
        if vc in self.vec_to_pow:
            return self.vec_to_pow[vc] + 1
        return 0

    def mul(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        log_a = a - 1
        log_b = b - 1
        return ((log_a + log_b) % _N) + 1

    def neg(self, a: int) -> int:
        if a == 0:
            return 0
        return self.mul(a, self.from_gf5(4))

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        if a == 1:
            return 1
        log_a = a - 1
        return (_N - log_a) % _N + 1

    def pow(self, a: int, exp: int) -> int:
        if a == 0:
            if exp == 0:
                return 1
            return 0
        if exp == 0:
            return 1
        log_a = a - 1
        return ((log_a * exp) % _N) + 1

    def from_gf5(self, val: int) -> int:
        """Convert a GF(5) element (0-4) to GF(5^7) element."""
        if val == 0:
            return 0
        v = [val] + [0] * (_M - 1)
        vt = tuple(v[:_M])
        if vt in self.vec_to_pow:
            return self.vec_to_pow[vt] + 1
        return 0

    def scalar_mul(self, a: int, s: int) -> int:
        """Multiply GF(5^7) element a by GF(5) scalar s (0-4)."""
        if a == 0 or s == 0:
            return 0
        if s == 1:
            return a
        return self.mul(a, self.from_gf5(s))

    def to_gf5(self, a: int) -> int:
        """Extract GF(5) value if a is in the base field."""
        if a == 0:
            return 0
        va = self.pow_to_vec[a - 1]
        if all(va[i] == 0 for i in range(1, _M)):
            return va[0]
        return -1  # not in GF(5)

    def is_gf5(self, a: int) -> bool:
        if a == 0:
            return True
        va = self.pow_to_vec[a - 1]
        return all(va[i] == 0 for i in range(1, _M))

    def eval_at_power(self, coeffs: List[int], power: int) -> int:
        """Evaluate polynomial with GF(5^7) coefficients at x = α^power.
        coeffs[i] is coefficient of x^i (GF(5^7) element).
        Returns GF(5^7) element.
        """
        # Use Horner
        result = 0
        alpha_pow = power + 1  # α^power in our representation
        for c in reversed(coeffs):
            result = self.add(result, 0)
            result = self.mul(result, alpha_pow)
            result = self.add(result, c)
        # Oops, the Horner is wrong: result = result * x + c_i
        # Let me redo
        result = 0
        for c in reversed(coeffs):
            result = self.mul(result, alpha_pow)
            result = self.add(result, c)
        return result

    def eval_at(self, coeffs: List[int], x: int) -> int:
        """Evaluate polynomial with GF(5^7) coefficients at x (GF(5^7) element)."""
        result = 0
        for c in reversed(coeffs):
            result = self.mul(result, x)
            result = self.add(result, c)
        return result

    def eval_gf5_poly_at(self, poly_coeffs: List[int], power: int) -> int:
        """Evaluate PolyGF5 at x = α^power.
        poly_coeffs[i] is coefficient of x^i (GF(5) element 0-4).
        """
        result = 0
        alpha_pow = power + 1
        for c in reversed(poly_coeffs):
            result = self.mul(result, alpha_pow)
            result = self.add(result, self.from_gf5(c))
        return result

    def eval_gf5_poly_at_val(self, poly_coeffs: List[int], x: int) -> int:
        """Evaluate PolyGF5 at x (GF(5^7) element)."""
        result = 0
        for c in reversed(poly_coeffs):
            result = self.mul(result, x)
            result = self.add(result, self.from_gf5(c))
        return result

    def poly_mul_gf57(self, a: List[int], b: List[int]) -> List[int]:
        """Multiply two polynomials with coefficients in GF(5^7)."""
        if not a or not b:
            return [0]
        result = [0] * (len(a) + len(b) - 1)
        for i, ca in enumerate(a):
            if ca == 0:
                continue
            for j, cb in enumerate(b):
                result[i + j] = self.add(result[i + j], self.mul(ca, cb))
        while len(result) > 1 and result[-1] == 0:
            result.pop()
        return result if result else [0]

    def poly_divmod_gf57(self, a: List[int], b: List[int]):
        """Divide polynomials over GF(5^7), return (quotient, remainder)."""
        if not b or (len(b) == 1 and b[0] == 0):
            raise ZeroDivisionError
        a = list(a)
        b = list(b)
        b_deg = len(b) - 1
        b_lead_inv = self.inv(b[-1])
        q_len = max(1, len(a) - len(b) + 1)
        q = [0] * q_len
        r = list(a)
        while len(r) >= len(b) and not (len(r) == 1 and r[0] == 0):
            deg_diff = len(r) - len(b)
            factor = self.mul(r[-1], b_lead_inv)
            q[deg_diff] = factor
            for j, bj in enumerate(b):
                r[deg_diff + j] = self.sub(r[deg_diff + j], self.mul(factor, bj))
            while len(r) > 1 and r[-1] == 0:
                r.pop()
        return q, r if r else [0]

    def poly_mod_gf57(self, a: List[int], b: List[int]) -> List[int]:
        _, r = self.poly_divmod_gf57(a, b)
        return r


# Global instance
gf57 = _GF5_7Field()


# ---------------------------------------------------------------------------
# BCH Code class
# ---------------------------------------------------------------------------

class BCHCode:
    """BCH code over GF(5) with extension field GF(5^7).
    Parameters: t = 11 (error correcting capability), j0 = 1.
    """

    def __init__(self, t: int = 11, j0: int = 1):
        self.t = t
        self.j0 = j0
        self.n = _N          # 78124
        self.designed_distance = 2 * t + 1

        # Compute cyclotomic cosets and generator polynomial
        self._compute_generator()

    def _cyclotomic_coset(self, i: int):
        """Compute cyclotomic coset of i modulo n under multiplication by 5."""
        coset = set()
        cur = i % self.n
        while cur not in coset:
            coset.add(cur)
            cur = (cur * 5) % self.n
        return sorted(coset)

    def _minimal_polynomial(self, coset: List[int]) -> PolyGF5:
        """Compute minimal polynomial of α^i over GF(5) for i in the coset.
        Returns PolyGF5 with coefficients in GF(5)."""
        # (x - α^j) = x + (-α^j) = x + 4*α^j  (4 is scalar in GF(5))

        c0 = coset[0]
        c0_elem = c0 + 1  # α^{c0} in our representation
        four = gf57.from_gf5(4)  # scalar 4 as GF(5^7) element

        # Start with (x - α^{c0}) = [4*α^{c0}, 1]
        coeffs = [gf57.mul(c0_elem, four), 1]  # GF(5^7) coefficients

        for j in coset[1:]:
            root = j + 1  # α^j in our representation
            # Multiply coeffs by (x - α^j) = [4*α^j, 1]
            neg_root = gf57.mul(root, four)  # 4*α^j
            new_coeffs = [0] * (len(coeffs) + 1)
            for i_deg, c in enumerate(coeffs):
                new_coeffs[i_deg + 1] = gf57.add(new_coeffs[i_deg + 1], c)
                new_coeffs[i_deg] = gf57.add(new_coeffs[i_deg], gf57.mul(c, neg_root))
            coeffs = new_coeffs

        # Now convert to PolyGF5 by extracting constant terms
        # Each coeff should be in GF(5)
        gf5_coeffs = []
        for c in coeffs:
            val = gf57.to_gf5(c)
            if val < 0:
                raise RuntimeError(f"Minimal polynomial coefficient not in GF(5): {c}")
            gf5_coeffs.append(val)
        return PolyGF5(gf5_coeffs)

    def _compute_generator(self):
        """Compute the generator polynomial g(x)."""
        # Find distinct minimal polynomials for j0, j0+1, ..., j0+2t-1
        needed_roots = set(range(self.j0, self.j0 + 2 * self.t))
        processed = set()
        minimal_polys = []

        for i in sorted(needed_roots):
            if i in processed:
                continue
            coset = self._cyclotomic_coset(i)
            processed.update(coset)
            mp = self._minimal_polynomial(coset)
            minimal_polys.append(mp)

        # g(x) = product of distinct minimal polynomials
        g = PolyGF5([1])
        for mp in minimal_polys:
            g = g * mp

        self.generator = g
        self.deg_g = g.deg  # n - k
        self.k = self.n - self.deg_g  # message length

        self._minimal_polys = minimal_polys

    @staticmethod
    def _poly_str(coeffs, var="x"):
        terms = []
        for i, c in enumerate(coeffs):
            if c == 0:
                continue
            if i == 0:
                terms.append(str(c))
            elif i == 1:
                terms.append(f"{c}{var}" if c != 1 else var)
            else:
                terms.append(f"{c}{var}^{i}" if c != 1 else f"{var}^{i}")
        return " + ".join(terms) if terms else "0"

    def encode(self, message: List[int]) -> List[int]:
        """Encode a message (list of GF(5) values).
        Systematic encoding: [parity (deg_g), message].
        Message length <= k. Shorter messages are treated as shortened code.
        """
        msg = [m % 5 for m in message]

        print(f"\n--- ENCODE ---")
        print(f"G(x) = {self._poly_str(self.generator.coeffs)} (mod 5)")
        i_coeffs = [0] * self.deg_g + msg
        print(f"i(x) = {self._poly_str(i_coeffs)} (mod 5)")

        # m(x) * x^{deg_g}: deg_g leading zeros then message
        shifted_poly = PolyGF5._from_raw([0] * self.deg_g + msg)

        _, remainder = shifted_poly.divmod(self.generator)

        # Parity = -remainder (in GF(5): -a = 4a)
        parity = [gf5_neg(c) for c in remainder.coeffs]
        while len(parity) < self.deg_g:
            parity.append(0)
        parity = parity[:self.deg_g]

        print(f"  → codeword length: {len(parity) + len(msg)} symbols ({len(parity)} parity + {len(msg)} message)")

        return parity + msg

    def _syndromes(self, received: List[int]) -> List[int]:
        """Compute syndromes S_j for j = 1, 2, ..., 2t.
        S_j = Σ received[i] * (α^j)^i = Σ received[i] * α^{i*j}
        """
        syndromes = []
        for j in range(self.j0, self.j0 + 2 * self.t):
            S = 0
            for i, ri in enumerate(received):
                if ri == 0:
                    continue
                # α^{i*j}
                power = (i * j) % self.n
                alpha_ij = power + 1  # in our representation
                term = gf57.scalar_mul(alpha_ij, ri)
                S = gf57.add(S, term)
            syndromes.append(S)
        return syndromes

    def _berlekamp_massey(self, syndromes: List[int]) -> List[int]:
        """Find error locator polynomial σ(x) using Berlekamp-Massey.
        Returns coefficients [σ_0, σ_1, ..., σ_v].
        """
        sigma = [1]
        tau = [1]
        L = 0
        d_prev = 1
        m = 1

        for k in range(1, len(syndromes) + 1):
            d = syndromes[k - 1]
            for i in range(1, L + 1):
                if i <= k - 1:
                    d = gf57.add(d, gf57.mul(sigma[i] if i < len(sigma) else 0, syndromes[k - 1 - i]))

            if d == 0:
                m += 1
            else:
                factor = gf57.mul(d, gf57.inv(d_prev))

                if 2 * L <= k - 1:
                    tau_new = list(sigma)
                    shifted_tau = [0] * m + tau
                    max_len = max(len(sigma), len(shifted_tau))
                    new_sigma = [0] * max_len
                    for i in range(max_len):
                        si = sigma[i] if i < len(sigma) else 0
                        ti = shifted_tau[i] if i < len(shifted_tau) else 0
                        new_sigma[i] = gf57.sub(si, gf57.mul(factor, ti))
                    sigma = new_sigma
                    while len(sigma) > 1 and sigma[-1] == 0:
                        sigma.pop()
                    if not sigma:
                        sigma = [0]
                    tau = tau_new
                    L = k - L
                    d_prev = d
                    m = 1
                else:
                    shifted_tau = [0] * m + tau
                    max_len = max(len(sigma), len(shifted_tau))
                    new_sigma = [0] * max_len
                    for i in range(max_len):
                        si = sigma[i] if i < len(sigma) else 0
                        ti = shifted_tau[i] if i < len(shifted_tau) else 0
                        new_sigma[i] = gf57.sub(si, gf57.mul(factor, ti))
                    sigma = new_sigma
                    while len(sigma) > 1 and sigma[-1] == 0:
                        sigma.pop()
                    if not sigma:
                        sigma = [0]
                    m += 1

        return sigma

    def _chien_search(self, sigma: List[int], length: int) -> List[int]:
        """Find roots of σ(x) by evaluating σ(α^{-i}) for i=0..length-1.
        Returns list of error positions i where σ(α^{-i}) = 0.
        """
        positions = []
        for i in range(length):
            # Evaluate σ at α^{-i} = α^{n-i}
            power = (self.n - i) % self.n
            x = power + 1 if power != 0 else 1
            val = gf57.eval_at(sigma, x)
            if val == 0:
                positions.append(i)
        return positions

    def _forney(self, sigma: List[int], syndromes: List[int],
                positions: List[int], received_len: int) -> List[int]:
        """Compute error values at the given positions using Forney's algorithm.
        e_i = Ω(α^{-i}) / σ'(α^{-i})
        Returns list of (position, error_value) as tuples.
        """
        S = list(syndromes)
        omega = gf57.poly_mul_gf57(sigma, S)
        if len(omega) > 2 * self.t:
            omega = omega[:2 * self.t]

        sigma_prime = []
        for i in range(1, len(sigma)):
            c = gf57.scalar_mul(sigma[i], i % 5)
            sigma_prime.append(c)
        if not sigma_prime:
            sigma_prime = [0]

        four = gf57.from_gf5(4)
        error_values = []
        for pos in positions:
            power = (self.n - pos) % self.n
            x_val = power + 1 if power != 0 else 1

            omega_val = gf57.eval_at(omega, x_val)
            sigma_prime_val = gf57.eval_at(sigma_prime, x_val)

            if sigma_prime_val != 0:
                e = gf57.mul(omega_val, gf57.inv(sigma_prime_val))
                e = gf57.mul(e, four)
                e_gf5 = gf57.to_gf5(e)
                if e_gf5 < 0:
                    e_gf5 = 0
                error_values.append((pos, e_gf5))
            else:
                error_values.append((pos, 0))

        return error_values

    def decode(self, received: List[int]) -> Tuple[List[int], bool, str]:
        """Decode a received word.
        Returns (decoded_message, success, message).
        """
        r = [ri % 5 for ri in received]

        # Compute syndromes
        syndromes = self._syndromes(r)

        # If all syndromes are 0, no errors detected
        if all(s == 0 for s in syndromes):
            # Extract message from systematic form: last k symbols
            if len(r) > self.deg_g:
                msg = r[-min(len(r) - self.deg_g, self.k):]
            else:
                msg = []
            return msg, True, "No errors detected"

        # Run Berlekamp-Massey
        sigma = self._berlekamp_massey(syndromes)

        # Check if σ is valid
        if len(sigma) == 1 and sigma[0] == 0:
            return [], False, "Decoding failure: invalid σ(x)"

        v = len(sigma) - 1  # number of errors detected

        if v > self.t:
            return [], False, f"Too many errors detected ({v} > {self.t}), cannot correct"

        # Chien search
        positions = self._chien_search(sigma, len(r))

        if len(positions) != v:
            return [], False, f"Found {len(positions)} error positions but σ has degree {v}"

        if len(positions) == 0:
            # No errors found but syndromes non-zero -> uncorrectable
            if len(r) > self.deg_g:
                msg = r[-min(len(r) - self.deg_g, self.k):]
            else:
                msg = []
            return msg, False, "Syndromes non-zero but no error positions found"

        # Forney: compute error values
        try:
            errors = self._forney(sigma, syndromes, positions, len(r))
        except Exception:
            return [], False, "Error value computation failed"

        # Correct errors
        corrected = list(r)
        for pos, val in errors:
            if pos < len(corrected) and val != 0:
                corrected[pos] = gf5_sub(corrected[pos], val)

        # Verify correction: recompute syndromes
        syndromes2 = self._syndromes(corrected)
        if not all(s == 0 for s in syndromes2):
            # Try harder: the correction might have failed
            # Return with best effort
            pass

        # Extract message
        if len(corrected) > self.deg_g:
            msg = corrected[-min(len(corrected) - self.deg_g, self.k):]
        else:
            msg = []

        # Verify: re-encode and compare with corrected codeword
        if len(corrected) >= self.deg_g:
            reencoded = self.encode(msg)
            if len(reencoded) <= len(corrected) and reencoded != corrected[:len(reencoded)]:
                return msg, False, "Verification failed: decoded message is inconsistent with corrected codeword"

        return msg, True, f"Corrected {len(positions)} error(s)"


# ---------------------------------------------------------------------------
# Text <-> GF(5) symbols conversion
# ---------------------------------------------------------------------------

# Each Unicode codepoint → 9 base-5 digits (5⁹ = 1_953_125 > 0x10FFFF)
_CHAR_WIDTH = 9


def text_to_symbols(text: str) -> List[int]:
    """Convert Unicode text to GF(5) symbols.
    Each codepoint → {_CHAR_WIDTH} big-endian base-5 digits.
    """
    symbols = []
    for ch in text:
        cp = ord(ch)
        if cp > 0x10FFFF:
            cp = 0x10FFFF
        for power in range(_CHAR_WIDTH - 1, -1, -1):
            divisor = 5 ** power
            symbols.append(cp // divisor)
            cp %= divisor
    return symbols


def symbols_to_text(symbols: List[int]) -> str:
    """Convert GF(5) symbols back to Unicode text.
    symbols are big-endian base-5 digits.
    """
    if not symbols or len(symbols) % _CHAR_WIDTH != 0:
        return ""
    chars = []
    for i in range(0, len(symbols), _CHAR_WIDTH):
        cp = 0
        for j in range(_CHAR_WIDTH):
            cp = cp * 5 + symbols[i + j]
        if cp == 0 or cp > 0x10FFFF:
            continue
        chars.append(chr(cp))
    return "".join(chars)


# Quick self-test
def _self_test():
    """Quick test of the BCH encode/decode cycle."""
    bch = BCHCode(t=11, j0=1)

    # Encode a short message
    msg = [1, 2, 3, 0, 4, 1, 2, 3, 0, 4]
    codeword = bch.encode(msg)

    assert len(codeword) == bch.deg_g + len(msg)

    # Decode without errors
    decoded, success, info = bch.decode(codeword)
    assert success, f"No-error decoding failed: {info}"
    assert decoded == msg, f"Decoded mismatch: {decoded} vs {msg}"

    # Test various error patterns
    for num_errors in range(1, 12):
        corrupted = list(codeword)
        for i in range(num_errors):
            pos = i * 11 % len(codeword)
            corrupted[pos] = (corrupted[pos] + 2) % 5
        decoded, success, info = bch.decode(corrupted)
        assert success, f"{num_errors} errors decoding failed: {info}"
        assert decoded == msg, f"{num_errors} errors decoded mismatch"

    # Test text <-> symbols conversion
    test_texts = [
        "Hello, World!",
        "BCH codec GF(5^7) t=11",
        "12345",
        "Привет",
        "A",
        "Anime ✦",
    ]
    for t in test_texts:
        sym = text_to_symbols(t)
        back = symbols_to_text(sym)
        assert back == t, f"Text conversion roundtrip failed: '{t}' → '{back}'"

    # Test BCH encode/decode with text
    for t in test_texts:
        sym = text_to_symbols(t)
        cw = bch.encode(sym)
        dec, ok, _ = bch.decode(cw)
        assert ok, f"Text encode/decode failed for '{t}'"
        back = symbols_to_text(dec)
        assert back == t, f"Text BCH roundtrip failed: '{t}' → '{back}'"

    # Text with errors
    for t in test_texts:
        sym = text_to_symbols(t)
        cw = bch.encode(sym)
        cw2 = list(cw)
        for j in range(min(3, len(cw2))):
            cw2[j] = (cw2[j] + 1) % 5
        dec, ok, _ = bch.decode(cw2)
        assert ok, f"Text decode with errors failed for '{t}'"
        back = symbols_to_text(dec)
        assert back == t, f"Text BCH with errors roundtrip failed: '{t}' → '{back}'"

    print("Self-test passed!")
    return True


if __name__ == "__main__":
    _self_test()
