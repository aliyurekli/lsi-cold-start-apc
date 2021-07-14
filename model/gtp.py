import mpdutils

from collections import Counter

from os import listdir
from os.path import join

from model import RecEngine


class GlobalTrackPopularity(RecEngine):
    def __init__(self, mpd, test):
        super().__init__()
        self.mpd = mpd
        self.test = test

        self.track_frequencies = Counter()
        self.__load()

    def __load(self):
        test_pids = mpdutils.get_pids_from_dataset_json(self.test)

        for file in [f for f in listdir(self.mpd) if f.endswith(".json")]:
            print("Loading gtp data from %s" % file)
            playlists = mpdutils.read_dataset_json(join(self.mpd, file))
            for p in playlists:
                if p["pid"] in test_pids:
                    continue

                for t in p["tracks"]:
                    self.track_frequencies[t["track_uri"]] +=1

    def recommend(self, p, n):
        return [a[0] for a in self.track_frequencies.most_common(n)]
