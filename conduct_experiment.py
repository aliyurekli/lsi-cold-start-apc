import argparse

from model import GlobalTrackPopularity
from model import NormalizedTitleMatching
from model import ClusterSimilarity


from experiment import Experimenter

CLI = argparse.ArgumentParser()

# obligatory params
CLI.add_argument("algorithm", choices=["ntm", "gtp", "csim"], help="Type of algorithm")
CLI.add_argument("test", help="Absolute path of the test json file")
CLI.add_argument("n", type=int, help="Number of recommendations per playlist")
CLI.add_argument("out", help="Absolute path of the recommendations csv file")

# optional params for gtp and ntm
CLI.add_argument("--mpd", help="Absolute path of the mpd data folder")

# optional params for csim
CLI.add_argument("--series", help="Absolute path of the mpd series txt file")
CLI.add_argument("--dictionary", help="Absolute path of the csim dictionary file")
CLI.add_argument("--lsi", help="Absolute path of the csim lsi file")
CLI.add_argument("--index", help="Absolute path of the csim index file")
CLI.add_argument("--sim_opt", choices=ClusterSimilarity.SIM_OPTS.keys(), help="Similarity strategy")
CLI.add_argument("--rank_opt", choices=ClusterSimilarity.RANK_OPTS.keys(), help="Ranking strategy")


if __name__ == '__main__':
    args = CLI.parse_args()

    algorithm, model = args.algorithm, None
    print("Building %s model..." % algorithm)

    if algorithm == "gtp":
        if args.mpd is None:
            raise RuntimeError("optional params failure")
        model = GlobalTrackPopularity(mpd=args.mpd, test=args.test)

    elif algorithm == "ntm":
        if args.mpd is None:
            raise RuntimeError("optional params failure")
        model = NormalizedTitleMatching(mpd=args.mpd, test=args.test)

    elif algorithm == "csim":
        mandatory = [args.series, args.dictionary, args.lsi, args.index, args.sim_opt, args.rank_opt]
        if len([m for m in mandatory if m is None]) > 0:
            raise RuntimeError("optional params failure")

        model = ClusterSimilarity(series=args.series,
                                  dictionary=args.dictionary,
                                  lsi=args.lsi,
                                  index=args.index,
                                  sim_opt=args.sim_opt,
                                  rank_opt=args.rank_opt)

    exp = Experimenter(model=model, test=args.test, n=args.n, out=args.out)
    exp.run()
