"""Interactive calculator for quadratics solved by integer factoring.

It looks for a factorization of the form (px + q)(rx + s) = 0,
then uses the zero-product property to report both roots.
"""

from fractions import Fraction


def divisors(number: int) -> list[int]:
    """Return every positive and negative integer divisor of a non-zero number."""
    values = []

    for value in range(1, abs(number) + 1):
        if number % value == 0:
            values.extend((value, -value))

    return values


def format_fraction(value: Fraction) -> str:
    """Show whole-number answers without a denominator."""
    if value.denominator == 1:
        return str(value.numerator)
    return str(value)


def find_factors(a: int, b: int, c: int):
    """Find p, q, r, s for (px + q)(rx + s), if possible."""
    for p in divisors(a):
        r = a // p

        # If c = 0, then x is one of the factors.
        if c == 0:
            if b % p == 0:
                return p, 0, r, b // p
            continue

        for q in divisors(c):
            s = c // q

            # (px + q)(rx + s)
            # = prx² + (ps + qr)x + qs
            if p * s + q * r == b:
                return p, q, r, s

    return None


def factor_term(coefficient: int, constant: int) -> str:
    """Format a factor, for example: 2x - 3."""
    if constant == 0:
        return f"{coefficient}x"

    sign = "+" if constant > 0 else "-"
    return f"{coefficient}x {sign} {abs(constant)}"


def show_steps(a: int, b: int, c: int, p: int, q: int, r: int, s: int) -> None:
    """Show how the quadratic was solved."""
    first_factor = factor_term(p, q)
    second_factor = factor_term(r, s)

    answer_1 = Fraction(-q, p)
    answer_2 = Fraction(-s, r)

    print("\n--- Solution Steps ---")

    print(f"\n1. Original equation:")
    print(f"   {a}x² + ({b})x + ({c}) = 0")

    print(f"\n2. Factor the quadratic:")
    print(f"   ({first_factor})({second_factor}) = 0")

    print(f"\n3. Check the multiplication:")
    print(f"   ({p}x)({r}x) = {p * r}x²")
    print(f"   ({p}x)({s}) + ({q})({r}x) = {p * s}x + {q * r}x = {b}x")
    print(f"   ({q})({s}) = {q * s}")

    print("\n4. Set each factor equal to zero:")
    print(f"   {first_factor} = 0")
    print(f"   x = {format_fraction(answer_1)}")

    print(f"\n   {second_factor} = 0")
    print(f"   x = {format_fraction(answer_2)}")

    print("\n5. Final answers:")
    print(f"   x = {format_fraction(answer_1)} or x = {format_fraction(answer_2)}")


def main() -> None:
    print("Quadratic Factoring Calculator")
    print("Solve equations in the form: ax² + bx + c = 0")
    print("Enter integer coefficients.\n")

    try:
        a = int(input("Enter a: "))
        b = int(input("Enter b: "))
        c = int(input("Enter c: "))
    except ValueError:
        print("Please enter whole numbers only.")
        return

    if a == 0:
        print("This is not a quadratic equation because a cannot be 0.")
        return

    factors = find_factors(a, b, c)

    if factors is None:
        print("\nThis equation does not factor using integer binomials.")
        print("Use the quadratic formula to solve this equation.")
        return

    p, q, r, s = factors

    answer_1 = Fraction(-q, p)
    answer_2 = Fraction(-s, r)

    print("\n--- Answer ---")
    print(f"Factored form: ({factor_term(p, q)})({factor_term(r, s)}) = 0")
    print(f"x = {format_fraction(answer_1)}")
    print(f"x = {format_fraction(answer_2)}")

    show_work = input("\nShow solution steps? (y/n): ").strip().lower()

    if show_work in {"y", "yes"}:
        show_steps(a, b, c, p, q, r, s)


if __name__ == "__main__":
    main()