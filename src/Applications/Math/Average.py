def get_numbers():
    """Ask the user for as many numbers as they want."""
    numbers = []

    while True:
        user_input = input(
            "Enter a number, or type 'done' to calculate the average: "
        ).strip().lower()

        if user_input == "done":
            break

        try:
            number = float(user_input)
            numbers.append(number)
        except ValueError:
            print("Please enter a valid number or type 'done'.")

    return numbers


def calculate_average(numbers):
    """Calculate and return the average of a list of numbers."""
    if len(numbers) == 0:
        return None

    total = sum(numbers)
    average = total / len(numbers)

    return average


def show_solution_steps(numbers, average):
    """Display how the average was calculated."""
    total = sum(numbers)
    amount = len(numbers)

    print("\n--- Solution Steps ---")
    print("Numbers entered:", numbers)
    print(f"Add the numbers: {total}")
    print(f"Count the numbers: {amount}")
    print(f"Average = total ÷ amount")
    print(f"Average = {total} ÷ {amount}")
    print(f"Average = {average}")


def main():
    print("Average Calculator")
    print("Enter as many numbers as you would like.")

    numbers = get_numbers()


    if len(numbers) == 0:
        print("\nNo numbers were entered.")
        return

    average = calculate_average(numbers)

    print("\n--- Answer ---")
    print(f"The average is: {average}")

    show_work = input("\nShow solution steps? (y/n): ").strip().lower()

    if show_work in {"y", "yes"}:
        show_solution_steps(numbers, average)


if __name__ == "__main__":
    main()