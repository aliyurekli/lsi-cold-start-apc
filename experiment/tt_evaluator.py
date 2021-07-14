import csv
import mpdutils
import numpy as np
import statistics


from collections import OrderedDict, defaultdict


def rprecision(targets, predictions, k):
    predictions = predictions[:k]
    target_set = set(targets)
    target_count = len(target_set)
    return float(len(set(predictions[:target_count]).intersection(target_set))) / target_count


def dcg(relevant_elements, retrieved_elements, k):
    retrieved_elements = list(OrderedDict.fromkeys(retrieved_elements[:k]))
    relevant_elements = list(OrderedDict.fromkeys(relevant_elements))

    if len(relevant_elements) == 0 or len(retrieved_elements) == 0:
        return 0.0

    score = [float(el in relevant_elements) for el in retrieved_elements]
    return np.sum(np.divide(score, np.log2(1 + np.arange(1, len(score) + 1))))


def ndcg(relevant_elements, retrieved_elements, k):
    idcg = dcg(relevant_elements, relevant_elements, min(k, len(relevant_elements)))

    if idcg == 0:
        raise ValueError("relevant_elements is empty, the metric is not defined")

    true_dcg = dcg(relevant_elements, retrieved_elements, k)
    return true_dcg / idcg


def recall(targets, predictions, k):
    predictions = predictions[:k]
    target_set = set(targets)
    target_count = len(target_set)
    return float(len(set(predictions).intersection(target_set))) / target_count


class Evaluator:
    def __init__(self, test, verbose):
        self.verbose = verbose
        self.holdouts = self.__load_holdouts(test)

    @staticmethod
    def __load_holdouts(test):
        data = dict()
        playlists = mpdutils.read_dataset_json(test)
        for p in playlists:
            data[p["pid"]] = [t["track_uri"] for t in p["holdouts"]]
        return data

    @staticmethod
    def __load_recommendations(path):
        data = defaultdict(lambda: [])
        with open(path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                data[int(row[0])].append(row[1])
        return data

    def evaluate(self, path, n):
        recommendations = self.__load_recommendations(path)
        rprecisions, ndcgs, recalls, pids = [], [], [], []

        for pid, recs in recommendations.items():
            targets = self.holdouts[pid]

            m1 = rprecision(targets, recs, n)
            m2 = ndcg(targets, recs, n)
            m3 = recall(targets, recs, n)

            rprecisions.append(m1)
            ndcgs.append(m2)
            recalls.append(m3)
            pids.append(pid)

        mean_rprecision = statistics.mean(rprecisions)
        mean_ndcg = statistics.mean(ndcgs)
        mean_recall = statistics.mean(recalls)

        print("%s\t%d\t%f\t%f\t%f" % (path, len(self.holdouts), mean_rprecision, mean_ndcg, mean_recall))

        if self.verbose:
            with open(path.replace(".csv", "-verbose.csv"), "w") as o:
                writer = csv.writer(o)
                for i in range(len(pids)):
                    writer.writerow([pids[i], rprecisions[i], ndcgs[i], recalls[i]])
