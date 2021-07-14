import argparse

from os import listdir
from os.path import join

from experiment import Evaluator

CLI = argparse.ArgumentParser()
CLI.add_argument("test", help="Absolute path of the test json file")
CLI.add_argument("n", type=int, help="Number of recommendations per playlist")
CLI.add_argument("recs", help="Absolute path of recommendations directory")
CLI.add_argument("verbose", type=int, choices=[0,1], help="Verbosity of evaluation")


if __name__ == '__main__':
    args = CLI.parse_args()

    eval = Evaluator(test=args.test, verbose=args.verbose)

    for file in [f for f in listdir(args.recs) if f.endswith(".csv")]:
        eval.evaluate(path=join(args.recs, file), n=args.n)

