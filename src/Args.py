import argparse

class Args:
    def __init__(self):
        parser = argparse.ArgumentParser(
        description="Generate a prompting challenge problem statement for a given theme."
        )
        parser.add_argument(
        "--theme",
        required=True,
        help="Theme to focus the prompting challenge around."
        )
        parser.add_argument(
        "--tcCount",
        required=False,
        default=50,
        help="How many test cases the challenge should have."
        )
        args = parser.parse_args()

        self.theme = args.theme.strip()
        if not self.theme:
            raise ValueError("Theme cannot be empty.")

        self.test_case_count = int(args.tcCount)