import mpdutils

from collections import defaultdict, Counter

from os import listdir
from os.path import join

from model import RecEngine

from titleutils import normalize


class NormalizedTitleMatching(RecEngine):
    def __init__(self, mpd, test):
        super().__init__()
        self.mpd = mpd
        self.test = test

        self.title_memberships = defaultdict(lambda: Counter())
        self.track_frequencies = Counter()
        self.__load()

    def __load(self):
        test_pids = mpdutils.get_pids_from_dataset_json(self.test)

        for file in [f for f in listdir(self.mpd) if f.endswith(".json")]:
            print("Loading ntm data from %s" % file)
            playlists = mpdutils.read_dataset_json(join(self.mpd, file))
            for p in playlists:
                if p["pid"] in test_pids:
                    continue

                nt = normalize(p["name"])
                for t in p["tracks"]:
                    self.title_memberships[nt][t["track_uri"]] += 1
                    self.track_frequencies[t["track_uri"]] += 1

    def recommend(self, p, n):
        nt = normalize(p["name"])
        recommendations = [a[0] for a in self.title_memberships[nt].most_common(n)]

        if n > len(recommendations):
            self.fallback(recommendations, n)

        return recommendations

    def fallback(self, recommendations, n):
        populars = [a[0] for a in self.track_frequencies.most_common(n)]
        required = [t for t in populars if t not in recommendations][:n-len(recommendations)]
        recommendations.extend(required)
