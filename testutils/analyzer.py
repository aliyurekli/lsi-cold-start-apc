import mpdutils
import statistics

from collections import defaultdict

from tabulate import tabulate


class TestAnalyzer:
    headers = ["category", "instances", "avg tracks", "avg samples", "avg holdouts"]

    def __init__(self, test):
        self.test = test

    def analyze(self):
        if self.test.endswith(".json"):
            print("Analyzing %s" % self.test)

            summary, stats = [], defaultdict(lambda: dict(instances=0, num_tracks=[], num_samples=[], num_holdouts=[]))
            for p in mpdutils.read_dataset_json(self.test):
                cid = p["category"]
                stats[cid]["instances"] += 1
                stats[cid]["num_tracks"].append(p["num_tracks"])
                stats[cid]["num_samples"].append(p["num_samples"])
                stats[cid]["num_holdouts"].append(p["num_holdouts"])

            total, all_tracks, all_samples, all_holdouts = 0, [], [], []

            for k, v in sorted(stats.items()):
                summary.append([k, v["instances"], statistics.mean(v["num_tracks"]), statistics.mean(v["num_samples"]), statistics.mean(v["num_holdouts"])])
                total += v["instances"]

                all_tracks.extend(v["num_tracks"])
                all_samples.extend(v["num_samples"])
                all_holdouts.extend(v["num_holdouts"])

            summary.append(["overall", total, statistics.mean(all_tracks), statistics.mean(all_samples), statistics.mean(all_holdouts)])

            print(tabulate(summary, headers=self.headers))
            print()
