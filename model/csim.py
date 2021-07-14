import math
import mpdutils
import statistics

from abc import ABC, abstractmethod

from collections import defaultdict, Counter

from model import RecEngine

from os import listdir
from os.path import join

from titleutils import LookupNormalization

from gensim.corpora import Dictionary
from gensim.models import LsiModel
from gensim.similarities import MatrixSimilarity


class LookupBasedSerializer:
    def __init__(self, mpd, test, out):
        self.mpd = mpd
        self.test = test
        self.out = out

    def serialize(self):
        test_pids = mpdutils.get_pids_from_dataset_json(self.test)
        norm = LookupNormalization()

        data = defaultdict(lambda: [])
        for file in [f for f in listdir(self.mpd) if f.endswith(".json")]:
            print("Converting playlists from %s" % file)
            playlists = mpdutils.read_dataset_json(join(self.mpd, file))
            for p in playlists:
                if p["pid"] in test_pids:
                    continue

                lu = norm.lookup(p["name"])
                tracks = [t["track_uri"] for t in p["tracks"]]
                data[lu].extend(tracks)

        with open(self.out, "w", encoding="utf-8") as o:
            for k, v in data.items():
                o.write(k)
                o.write("\t")
                o.write(" ".join(v))
                o.write("\n")


class SerializationReader:
    def __init__(self, series):
        self.series = series

    def read(self):
        documents, doc2idx, idx2doc = [], {}, {}
        with open(self.series, "r", encoding="utf-8") as f:
            idx = 0
            for line in f:
                tmp = line.replace("\n", "").split("\t")
                doc_name = tmp[0]
                tracks = tmp[1].split(" ")

                documents.append(tracks)
                doc2idx[doc_name] = idx
                idx2doc[idx] = doc_name
                idx += 1

        return documents, doc2idx, idx2doc


class LsiTrainer:
    def __init__(self, series, dimensions, dictionary, lsi, index):
        self.series = series
        self.dimensions = dimensions
        self.dictionary = dictionary
        self.lsi = lsi
        self.index = index

    def train(self):
        print("Reading serializations...")
        sr = SerializationReader(self.series)
        documents, doc2idx, idx2doc = sr.read()

        print("Building dictionary...")
        dictionary = Dictionary(documents)
        corpus = [dictionary.doc2bow(doc) for doc in documents]

        print("Building model...")
        lsi = LsiModel(corpus, id2word=dictionary, num_topics=self.dimensions)

        print("Building index...")
        index = MatrixSimilarity(lsi[corpus])

        print("Saving...")
        dictionary.save(self.dictionary)
        lsi.save(self.lsi)
        index.save(self.index)


class RankingStrategy(ABC):

    INITIAL_DROP = 0.05

    def __init__(self):
        pass

    @abstractmethod
    def candidate_tracks(self, dictionary: Dictionary, clusters, documents, n):
        pass

    @staticmethod
    def initial_rank(documents, clusters, n):
        initials = []

        if len(clusters) > 1:
            c1, c2 = clusters[0], clusters[1]
            c1_doc = documents[c1[0]]

            drop = c1[1] - c2[1]

            if drop > RankingStrategy.INITIAL_DROP and len(set(c1_doc)) < n:
                initials = [t[0] for t in Counter(c1_doc).most_common(n)]

        return initials


class RawTF(RankingStrategy):
    """ track ranking based on term frequency """

    def __init__(self):
        super().__init__()

    def candidate_tracks(self, dictionary, clusters, documents, n):
        tf = Counter()

        for doc_idx in [c[0] for c in clusters]:
            doc = documents[doc_idx]
            vec_bow = dictionary.doc2bow(doc)

            tf += Counter(dict(zip([v[0] for v in vec_bow], [v[1] for v in vec_bow])))

        initials = self.initial_rank(documents, clusters, n)
        rankings = [dictionary.id2token[t[0]] for t in tf.most_common(n) if dictionary.id2token[t[0]] not in initials][:n-len(initials)]
        return initials + rankings


class RawTFxIDF(RankingStrategy):
    """ track ranking based on term frequency * inverse document frequency """

    def __init__(self):
        super().__init__()

    def candidate_tracks(self, dictionary, clusters, documents, n):
        tf = Counter()

        for doc_idx in [c[0] for c in clusters]:
            doc = documents[doc_idx]
            vec_bow = dictionary.doc2bow(doc)

            tf += Counter(dict(zip([v[0] for v in vec_bow], [v[1] for v in vec_bow])))

        tfidfs = [(t, tf[t] * (math.log(len(documents) / dictionary.dfs[t]))) for t in tf]

        initials = self.initial_rank(documents, clusters, n)
        rankings = [dictionary.id2token[t[0]] for t in sorted(tfidfs, key=lambda tup: tup[1], reverse=True) if dictionary.id2token[t[0]] not in initials][:n-len(initials)]
        return initials + rankings


class WeightedTF(RankingStrategy):
    """ track ranking based on cluster similarity * term frequency """

    def __init__(self):
        super().__init__()

    def candidate_tracks(self, dictionary, clusters, documents, n):
        scores = defaultdict(float)

        for doc_idx, doc_score in clusters:
            doc = documents[doc_idx]
            vec_bow = dictionary.doc2bow(doc)

            for token_id, freq in vec_bow:
                scores[token_id] += doc_score * freq

        initials = self.initial_rank(documents, clusters, n)
        rankings = [dictionary.id2token[t[0]] for t in sorted(scores.items(), key=lambda x: x[1], reverse=True) if dictionary.id2token[t[0]] not in initials][:n-len(initials)]
        return initials + rankings


class MaxWeightedTF(RankingStrategy):
    """ track ranking based on max cluster similarity * term frequency """

    def __init__(self):
        super().__init__()

    def candidate_tracks(self, dictionary, clusters, documents, n):
        tokens = defaultdict(lambda: [0, -1])

        for doc_idx, doc_score in clusters:
            doc = documents[doc_idx]
            vec_bow = dictionary.doc2bow(doc)

            for token_id, freq in vec_bow:
                if doc_score > tokens[token_id][1]:
                    tokens[token_id][1] = doc_score
                tokens[token_id][0] += freq

        initials = self.initial_rank(documents, clusters, n)
        rankings = [dictionary.id2token[t[0]] for t in sorted(tokens.items(), key=lambda item: item[1][0] * item[1][1], reverse=True) if dictionary.id2token[t[0]] not in initials][:n-len(initials)]
        return initials + rankings


class SimilarityStrategy(ABC):
    def __init__(self, constant):
        self.constant = constant

    @abstractmethod
    def candidate_clusters(self, documents, similarities, n):
        pass


class AdaptiveThreshold(SimilarityStrategy):

    CUTOFF = 10

    def __init__(self, constant):
        super().__init__(constant)

    def candidate_clusters(self, documents, similarities, n):
        clusters, unique_tracks = [], set()

        above_threshold = [s for s in similarities if s[1] >= self.constant]
        mean = statistics.mean([a[1] for a in above_threshold])

        for s in similarities:
            doc_idx, doc_score = s

            if (doc_score < mean * self.constant and len(unique_tracks) >= n) or len(clusters) == self.CUTOFF:
                break

            clusters.append(s)
            unique_tracks = unique_tracks.union(set(documents[doc_idx]))

        return clusters


class Threshold(SimilarityStrategy):
    def __init__(self, constant):
        super().__init__(constant)

    def candidate_clusters(self, documents, similarities, n):
        clusters, unique_tracks = [], set()

        for s in similarities:
            doc_idx, doc_score = s

            if doc_score < self.constant and len(unique_tracks) >= n:
                break

            clusters.append(s)
            unique_tracks = unique_tracks.union(set(documents[doc_idx]))

        return clusters


class Neighborhood(SimilarityStrategy):
    def __init__(self, constant):
        super().__init__(constant)

    def candidate_clusters(self, documents, similarities, n):
        clusters, unique_tracks = [], set()

        for s in similarities:
            if len(clusters) >= self.constant and len(unique_tracks) >= n:
                break

            doc_idx = s[0]
            clusters.append(s)
            unique_tracks = unique_tracks.union(set(documents[doc_idx]))

        return clusters


class ClusterSimilarity(RecEngine):

    SIM_OPTS = {
        "at99": dict(cls="AdaptiveThreshold", constant=0.99),
        "at98": dict(cls="AdaptiveThreshold", constant=0.98),
        "at97": dict(cls="AdaptiveThreshold", constant=0.97),
        "at96": dict(cls="AdaptiveThreshold", constant=0.96),
        "at95": dict(cls="AdaptiveThreshold", constant=0.95),
        "at94": dict(cls="AdaptiveThreshold", constant=0.94),
        "at93": dict(cls="AdaptiveThreshold", constant=0.93),
        "at92": dict(cls="AdaptiveThreshold", constant=0.92),
        "at91": dict(cls="AdaptiveThreshold", constant=0.91),
        "at90": dict(cls="AdaptiveThreshold", constant=0.90),

        "t99": dict(cls="Threshold", constant=0.99),
        "t98": dict(cls="Threshold", constant=0.98),
        "t97": dict(cls="Threshold", constant=0.97),
        "t96": dict(cls="Threshold", constant=0.96),
        "t95": dict(cls="Threshold", constant=0.95),
        "t94": dict(cls="Threshold", constant=0.94),
        "t93": dict(cls="Threshold", constant=0.93),
        "t92": dict(cls="Threshold", constant=0.92),
        "t91": dict(cls="Threshold", constant=0.91),
        "t90": dict(cls="Threshold", constant=0.90),

        "n10": dict(cls="Neighborhood", constant=10),
        "n9": dict(cls="Neighborhood", constant=9),
        "n8": dict(cls="Neighborhood", constant=8),
        "n7": dict(cls="Neighborhood", constant=7),
        "n6": dict(cls="Neighborhood", constant=6),
        "n5": dict(cls="Neighborhood", constant=5),
        "n4": dict(cls="Neighborhood", constant=4),
        "n3": dict(cls="Neighborhood", constant=3),
        "n2": dict(cls="Neighborhood", constant=2),
        "n1": dict(cls="Neighborhood", constant=1),
    }

    RANK_OPTS = {
        "rawtf": "RawTF",
        "wtf": "WeightedTF",
        "maxwtf": "MaxWeightedTF",
        "rawtfidf": "RawTFxIDF"
    }

    def __init__(self, series, dictionary, lsi, index, sim_opt, rank_opt):
        super().__init__()

        self.norm = LookupNormalization()

        self.dictionary: Dictionary = Dictionary.load(dictionary)
        self.lsi: LsiModel = LsiModel.load(lsi)
        self.index: MatrixSimilarity = MatrixSimilarity.load(index)

        sr = SerializationReader(series)
        self.documents, self.doc2idx, self.idx2doc = sr.read()

        sim_class = globals()[self.SIM_OPTS[sim_opt]["cls"]]
        self.sim_strategy: SimilarityStrategy = sim_class(self.SIM_OPTS[sim_opt]["constant"])

        rank_class = globals()[self.RANK_OPTS[rank_opt]]
        self.rank_strategy: RankingStrategy = rank_class()

    def recommend(self, p, n):
        doc_name = self.norm.lookup(p["name"])

        if doc_name in self.doc2idx:
            doc_idx = self.doc2idx[doc_name]
        else:
            doc_idx = 0

        doc = self.documents[doc_idx]
        vec_bow = self.dictionary.doc2bow(doc)
        vec_lsi = self.lsi[vec_bow]

        similarities = self.index[vec_lsi]
        similarities = sorted(enumerate(similarities), key=lambda item: -item[1])

        # clusters as (doc index, score) tuples
        clusters = self.sim_strategy.candidate_clusters(self.documents, similarities, n)
        tracks = self.rank_strategy.candidate_tracks(self.dictionary, clusters, self.documents, n)

        return tracks
