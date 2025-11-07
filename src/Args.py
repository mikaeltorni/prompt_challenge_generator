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
        parser.add_argument(
        "--alias",
        required=False,
        help="Optional directory name prefix for the generated challenge."
        )
        parser.add_argument(
        "--n",
        type=int,
        default=1,
        help="How many challenges to generate for the provided theme."
        )
        parser.add_argument(
        "--max_concurrent",
        type=int,
        default=1,
        help="Maximum number of simultaneous challenge generations."
        )
        args = parser.parse_args()

        self.theme = args.theme.strip()
        if not self.theme:
            raise ValueError("Theme cannot be empty.")

        if args.alias is not None:
            alias = args.alias.strip()
            if not alias:
                raise ValueError("Alias cannot be empty when provided.")
            self.alias = alias
        else:
            self.alias = None

        self.test_case_count = int(args.tcCount)

        self.n = int(args.n)
        if self.n < 1:
            raise ValueError("--n must be greater than or equal to 1.")

        self.max_concurrent = int(args.max_concurrent)
        if self.max_concurrent < 1:
            raise ValueError("--max_concurrent must be greater than or equal to 1.")
