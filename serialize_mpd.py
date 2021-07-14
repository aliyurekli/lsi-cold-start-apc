import argparse

from model import LookupBasedSerializer

CLI = argparse.ArgumentParser()
CLI.add_argument("mpd", help="Absolute path of the mpd data folder")
CLI.add_argument("test", help="Absolute path of the test json file")
CLI.add_argument("out", help="Absolute path of the output txt file")


if __name__ == '__main__':
    args = CLI.parse_args()

    lbs = LookupBasedSerializer(mpd=args.mpd, test=args.test, out=args.out)
    lbs.serialize()
