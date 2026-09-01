"""
BCH code over GF(5^7) with t=11 and j0=1.
Primitive polynomial: x^7 + 3x + 3 (Conway polynomial)
"""


class GaloisField:
    P = 5
    M = 7
    SIZE = P ** M
    ORDER = SIZE - 1
    POW5 = [1]
    for _ in range(M):
        POW5.append(POW5[-1] * P)

    def __init__(self):
        self.log: list[int | None] = [None] * self.SIZE
        self.antilog: list[int] = [0] * self.ORDER

        current = 1
        for exp in range(self.ORDER):
            self.antilog[exp] = current
            self.log[current] = exp
            current = self._mul_alpha(current)

    def _digit(self, a: int, k: int) -> int:
        return (a // self.POW5[k]) % self.P

    def _to_int(self, coeffs: tuple[int, ...]) -> int:
        result = 0
        for i, c in enumerate(coeffs):
            result += c * self.POW5[i]
        return result

    def _mul_alpha(self, a: int) -> int:
        if a == 0:
            return 0
        d0 = a % self.P
        d6 = (a // self.POW5[6]) % self.P
        return (
            ((2 * d6) % self.P)
            + ((d0 + 2 * d6) % self.P) * self.POW5[1]
            + ((a // self.POW5[1]) % self.P) * self.POW5[2]
            + ((a // self.POW5[2]) % self.P) * self.POW5[3]
            + ((a // self.POW5[3]) % self.P) * self.POW5[4]
            + ((a // self.POW5[4]) % self.P) * self.POW5[5]
            + ((a // self.POW5[5]) % self.P) * self.POW5[6]
        )

    def _to_tuple(self, a: int) -> tuple[int, ...]:
        return tuple((a // self.POW5[i]) % self.P for i in range(self.M))

    def add(self, a: int, b: int) -> int:
        if a == 0:
            return b
        if b == 0:
            return a
        result = 0
        for i in range(self.M):
            ai = (a // self.POW5[i]) % self.P
            bi = (b // self.POW5[i]) % self.P
            result += ((ai + bi) % self.P) * self.POW5[i]
        return result

    def sub(self, a: int, b: int) -> int:
        if b == 0:
            return a
        if a == 0:
            result = 0
            for i in range(self.M):
                bi = (b // self.POW5[i]) % self.P
                result += ((-bi) % self.P) * self.POW5[i]
            return result
        result = 0
        for i in range(self.M):
            ai = (a // self.POW5[i]) % self.P
            bi = (b // self.POW5[i]) % self.P
            result += ((ai - bi) % self.P) * self.POW5[i]
        return result

    def neg(self, a: int) -> int:
        if a == 0:
            return 0
        result = 0
        for i in range(self.M):
            ai = (a // self.POW5[i]) % self.P
            result += ((-ai) % self.P) * self.POW5[i]
        return result

    def mul(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        la = self.log[a]
        lb = self.log[b]
        return self.antilog[(la + lb) % self.ORDER]

    def div(self, a: int, b: int) -> int:
        if a == 0:
            return 0
        if b == 0:
            raise ValueError("Division by zero")
        return self.antilog[(self.log[a] - self.log[b]) % self.ORDER]

    def inv(self, a: int) -> int:
        if a == 0:
            raise ValueError("Cannot invert zero")
        return self.antilog[(-self.log[a]) % self.ORDER]

    def pow(self, a: int, n: int) -> int:
        if a == 0:
            if n == 0:
                return 1
            return 0
        if n == 0:
            return 1
        return self.antilog[(self.log[a] * n) % self.ORDER]

    def eval_poly(self, coeffs: list[int], x: int) -> int:
        result = 0
        for coeff in reversed(coeffs):
            result = self.mul(result, x)
            if coeff != 0:
                result = self.add(result, coeff)
        return result

    def poly_mul(self, a: list[int], b: list[int]) -> list[int]:
        result = [0] * (len(a) + len(b) - 1)
        for i, ca in enumerate(a):
            if ca == 0:
                continue
            for j, cb in enumerate(b):
                if cb == 0:
                    continue
                result[i + j] = self.add(result[i + j], self.mul(ca, cb))
        return result

    def poly_divmod(self, dividend: list[int], divisor: list[int]) -> tuple[list[int], list[int]]:
        dividend = list(dividend)
        divisor = list(divisor)

        while dividend and dividend[-1] == 0:
            dividend.pop()
        while divisor and divisor[-1] == 0:
            divisor.pop()

        if not divisor:
            raise ValueError("Division by zero polynomial")

        if len(dividend) < len(divisor):
            return [0], dividend

        quotient = [0] * (len(dividend) - len(divisor) + 1)
        remainder = list(dividend)

        for _ in range(len(quotient)):
            if len(remainder) < len(divisor):
                break
            deg_diff = len(remainder) - len(divisor)
            factor = self.div(remainder[-1], divisor[-1])
            quotient[deg_diff] = factor
            for j, c in enumerate(divisor):
                remainder[deg_diff + j] = self.sub(
                    remainder[deg_diff + j], self.mul(factor, c)
                )
            while remainder and remainder[-1] == 0:
                remainder.pop()

        return quotient, remainder if remainder else [0]

    def format(self, a: int) -> str:
        if a == 0:
            return "0"
        coeffs = self._to_tuple(a)
        terms = []
        for i in range(self.M):
            c = coeffs[i]
            if c != 0:
                if i == 0:
                    terms.append(str(c))
                elif i == 1:
                    terms.append(f"{c}α" if c != 1 else "α")
                else:
                    terms.append(f"{c}α^{i}" if c != 1 else f"α^{i}")
        return " + ".join(terms) if terms else "0"


class BCHCode:
    def __init__(self):
        self.gf = GaloisField()
        self.t = 11
        self.j0 = 1
        self.n = self.gf.ORDER
        self._compute_generator()
        self.k = self.n - (len(self.g) - 1)
        self.n_k = self.n - self.k

    def _compute_generator(self):
        gf = self.gf
        n = self.n
        needed_roots = set(range(self.j0, self.j0 + 2 * self.t))
        processed = set()
        self.g = [1]

        for r in needed_roots:
            if r in processed:
                continue
            coset = []
            x = r
            while x not in coset:
                coset.append(x)
                processed.add(x)
                x = (x * gf.P) % n

            mp = [1]
            for j in coset:
                alpha_j = gf.antilog[j % n]
                term = [gf.neg(alpha_j), 1]
                mp = gf.poly_mul(mp, term)

            self.g = gf.poly_mul(self.g, mp)

        while self.g and self.g[-1] == 0:
            self.g.pop()

    def encode(self, message: list[int]) -> list[int]:
        gf = self.gf

        if len(message) > self.k:
            raise ValueError(f"Message too long, max {self.k} symbols")

        msg = list(message) + [0] * (self.k - len(message))

        dividend = [0] * self.n_k + msg

        _, remainder = gf.poly_divmod(dividend, self.g)

        rem = remainder + [0] * (self.n_k - len(remainder))

        neg_rem = [gf.sub(0, r) for r in rem]

        return neg_rem + msg

    def _compute_syndromes(self, received: list[int]) -> list[int]:
        gf = self.gf
        syndromes = []
        for j in range(1, 2 * self.t + 1):
            s = gf.eval_poly(received, gf.antilog[j % self.n])
            syndromes.append(s)
        return syndromes

    def _berlekamp_massey(self, syndromes: list[int]) -> list[int]:
        gf = self.gf
        sigma = [1]
        B = [1]
        L = 0
        m = 1
        b = 1

        for r in range(1, 2 * self.t + 1):
            d = syndromes[r - 1]
            for i in range(1, L + 1):
                if i < len(sigma) and (r - 1 - i) >= 0:
                    term = gf.mul(sigma[i], syndromes[r - 1 - i])
                    d = gf.add(d, term)

            if d == 0:
                m += 1
            else:
                scaled_B = [0] * m + B
                factor = gf.div(d, b)
                T = list(sigma)
                for i in range(len(scaled_B)):
                    term = gf.mul(factor, scaled_B[i])
                    if i < len(T):
                        T[i] = gf.sub(T[i], term)
                    else:
                        T.append(gf.sub(0, term))

                if 2 * L >= r:
                    sigma = T
                    m += 1
                else:
                    B = list(sigma)
                    sigma = T
                    L = r - L
                    m = 1
                    b = d

        while sigma and sigma[-1] == 0:
            sigma.pop()
        return sigma

    def _chien_search(self, sigma: list[int]) -> list[int]:
        gf = self.gf
        error_positions = []
        for i in range(self.n):
            val = gf.eval_poly(sigma, gf.antilog[i % self.n])
            if val == 0:
                pos = (self.n - i) % self.n
                error_positions.append(pos)
        return sorted(set(error_positions))

    def _forney(self, syndromes: list[int], sigma: list[int],
                 error_positions: list[int]) -> list[int]:
        gf = self.gf
        if not error_positions:
            return []

        S = [0] + syndromes

        omega_deg = 2 * self.t - 1
        omega = [0] * (omega_deg + 1)

        for k in range(omega_deg + 1):
            val = 0
            for i in range(min(len(sigma), k + 1)):
                j = k - i + 1
                if 1 <= j <= 2 * self.t:
                    term = gf.mul(sigma[i], S[j])
                    val = gf.add(val, term)
            omega[k] = val

        error_values = []
        for pos in error_positions:
            X_l = gf.antilog[pos % self.n]
            X_l_inv = gf.inv(X_l)

            omega_val = gf.eval_poly(omega, X_l_inv)

            sigma_prime = []
            for i, coeff in enumerate(sigma):
                if i > 0:
                    coeff_i = gf.mul(coeff, i % gf.P)
                    sigma_prime.append(coeff_i)
            if not sigma_prime:
                sigma_prime = [0]

            sigma_prime_val = gf.eval_poly(sigma_prime, X_l_inv)

            if sigma_prime_val == 0:
                error_values.append(0)
            else:
                e_val = gf.div(omega_val, sigma_prime_val)
                e_val = gf.sub(0, e_val)
                error_values.append(e_val)

        return error_values

    def decode(self, received: list[int]) -> tuple[list[int], list[int], list[int]]:
        gf = self.gf
        syndromes = self._compute_syndromes(received)

        if all(s == 0 for s in syndromes):
            return received[self.n_k:], [], []

        sigma = self._berlekamp_massey(syndromes)
        v = len(sigma) - 1

        if v > self.t or v == 0:
            return received[self.n_k:], [], []

        error_positions = self._chien_search(sigma)

        if len(error_positions) != v:
            return received[self.n_k:], [], []

        error_values = self._forney(syndromes, sigma, error_positions)

        corrected = list(received)
        for pos, val in zip(error_positions, error_values):
            corrected[pos] = gf.sub(corrected[pos], val)

        return corrected[self.n_k:], error_positions, error_values
