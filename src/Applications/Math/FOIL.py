
"""Multiply as many binomials as you want.

Example:
(x + 2)(2x - 3)(x + 4)
"""

SUPERSCRIPTS = {
    2: "²",
    3: "³",
    4: "⁴",
    5: "⁵",
    6: "⁶",
    7: "⁷",
    8: "⁸",
    9: "⁹",
}


def exponent_text(power):
    """Return a readable exponent."""
    if power == 1:
        return ""
    if power in SUPERSCRIPTS:
        return SUPERSCRIPTS[power]
    return f"^{power}"


def monomial(coefficient, power):
    """Format one term, such as -3x² or 5x."""
    absolute_value = abs(coefficient)

    if power == 0:
        return str(absolute_value)

    if absolute_value == 1:
        return f"x{exponent_text(power)}"

    return f"{absolute_value}x{exponent_text(power)}"


def polynomial_to_string(coefficients):
    """
    Convert a coefficient list into a polynomial string.

    Example:
    [6, 5, 2] becomes 2x² + 5x + 6
    """
    terms = []

    for power in range(len(coefficients) - 1, -1, -1):
        coefficient = coefficients[power]

        if coefficient == 0:
            continue

        term = monomial(coefficient, power)

        if not terms:
            if coefficient < 0:
                terms.append("-" + term)
            else:
                terms.append(term)
        else:
            if coefficient < 0:
                terms.append("- " + term)
            else:
                terms.append("+ " + term)

    return " ".join(terms) if terms else "0"


def multiply_by_binomial(polynomial, x_coefficient, constant):
    """
    Multiply a polynomial by a binomial:

    polynomial × (x_coefficient*x + constant)
    """
    result = [0] * (len(polynomial) + 1)

    for power, coefficient in enumerate(polynomial):
        # Multiply by the constant.
        result[power] += coefficient * constant

        # Multiply by the x term.
        result[power + 1] += coefficient * x_coefficient

    return result


def show_steps(binomials):
    """Show the multiplication process one binomial at a time."""
    first_x, first_constant = binomials[0]
    current_polynomial = [first_constant, first_x]

    print("\n--- Solution Steps ---")
    print(f"Start with: ({polynomial_to_string(current_polynomial)})")

    for number, (x_coefficient, constant) in enumerate(binomials[1:], start=2):
        next_binomial = [constant, x_coefficient]

        print(f"\nStep {number - 1}: Multiply by ({polynomial_to_string(next_binomial)})")
        print(
            f"({polynomial_to_string(current_polynomial)})"
            f"({polynomial_to_string(next_binomial)})"
        )

        print("Distribute each term:")
        for power, coefficient in enumerate(current_polynomial):
            if coefficient == 0:
                continue

            current_term = polynomial_to_string(
                [0] * power + [coefficient]
            )

            print(
                f"  {current_term}({polynomial_to_string(next_binomial)})"
            )

        current_polynomial = multiply_by_binomial(
            current_polynomial,
            x_coefficient,
            constant
        )

        print(f"Result: {polynomial_to_string(current_polynomial)}")

    print("\nFinal answer:")
    print(polynomial_to_string(current_polynomial))


def main():
    print("Multiple Binomial FOIL Calculator")
    print("Multiply binomials in the form (ax + b).")

    try:
        amount = int(input("\nHow many binomials would you like to multiply? "))
    except ValueError:
        print("Please enter a whole number.")
        return

    if amount < 2:
        print("Please enter at least 2 binomials.")
        return

    binomials = []

    for number in range(1, amount + 1):
        print(f"\nBinomial {number}: (ax + b)")

        try:
            x_coefficient = int(input("Enter a (coefficient of x): "))
            constant = int(input("Enter b (constant): "))
        except ValueError:
            print("Please enter whole numbers only.")
            return

        if x_coefficient == 0:
            print("The coefficient of x cannot be 0.")
            return

        binomials.append((x_coefficient, constant))

    expression = "".join(
        f"({polynomial_to_string([constant, x_coefficient])})"
        for x_coefficient, constant in binomials
    )

    current_polynomial = [binomials[0][1], binomials[0][0]]

    for x_coefficient, constant in binomials[1:]:
        current_polynomial = multiply_by_binomial(
            current_polynomial,
            x_coefficient,
            constant
        )

    print("\n--- Answer ---")
    print(f"Expression: {expression}")
    print(f"Product: {polynomial_to_string(current_polynomial)}")

    show_work = input("\nShow solution steps? (y/n): ").strip().lower()

    if show_work in {"y", "yes"}:
        show_steps(binomials)


if __name__ == "__main__":
    main()