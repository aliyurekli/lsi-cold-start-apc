import argparse

from model import LsiTrainer

CLI = argparse.ArgumentParser()
CLI.add_argument("series", help="Absolute path of the mpd series txt file")
CLI.add_argument("dimensions", type=int, help="Dimension of lsi model")
CLI.add_argument("dictionary", help="Absolute path of the output dictionary file")
CLI.add_argument("lsi", help="Absolute path of the output lsi file")
CLI.add_argument("index", help="Absolute path of the output index file")


if __name__ == '__main__':
    args = CLI.parse_args()

    lt = LsiTrainer(series=args.series,
                    dimensions=args.dimensions,
                    dictionary=args.dictionary,
                    lsi=args.lsi,
                    index=args.index)
    lt.train()

