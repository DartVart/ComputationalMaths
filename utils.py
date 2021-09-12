def get_rounded_to_print(number, print_accuracy):
    return f"{number:.{print_accuracy}f}".rstrip("0").rstrip(".")
