import argparse

from testutils import TestAnalyzer

CLI = argparse.ArgumentParser()
CLI.add_argument("test", help="Absolute path of the test json file")

if __name__ == '__main__':
    args = CLI.parse_args()

    ta = TestAnalyzer(test=args.test)
    ta.analyze()
