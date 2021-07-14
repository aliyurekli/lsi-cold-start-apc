import random
import mpdutils
import json

from collections import defaultdict
from os import listdir
from os.path import join


class TestGen:
    def __init__(self, mpd, out, size, mode):
        self.mpd = mpd
        self.out = out
        self.size = size
        self.mode = mode

        self.current_frequencies = defaultdict(lambda: 0)
        self.reservations = []

    def _count_tracks(self):
        for f in [file for file in listdir(self.mpd) if file.endswith(".json")]:
            print("Counting track frequencies %s" % f)

            playlists = mpdutils.read_dataset_json(join(self.mpd, f))
            for p in playlists:
                tmp = set()
                for t in p["tracks"]:
                    track_uri = t["track_uri"]
                    if track_uri not in tmp:
                        self.current_frequencies[track_uri] += 1
                        tmp.add(track_uri)

    def _is_applicable(self, playlist):
        for t in playlist["tracks"]:
            track_uri = t["track_uri"]
            if not self.current_frequencies[track_uri] > 1:
                return False
        return True

    def _search(self, limit=100):
        low, up = mpdutils.COLD_START["lower"], mpdutils.COLD_START["upper"]

        files = [f for f in listdir(self.mpd) if f.endswith(".json")]
        random.shuffle(files)

        while True:
            file = files.pop()
            print("Searching for candidate playlists %s" % file)

            playlists = mpdutils.read_dataset_json(join(self.mpd, file))
            random.shuffle(playlists)

            candidates = [p for p in playlists if low <= p["num_tracks"]][:limit] if self.mode == "custom" \
                else [p for p in playlists if low <= p["num_tracks"] <= up][:limit]

            for c in candidates:
                if self._is_applicable(c):
                    pjson = dict(pid=c["pid"],
                                 name=c["name"],
                                 category=mpdutils.COLD_START["id"],
                                 num_tracks=c["num_tracks"],
                                 num_samples=mpdutils.COLD_START["seeds"],
                                 num_holdouts=c["num_tracks"],
                                 tracks=[],
                                 holdouts=sorted(c["tracks"], key=lambda x: x["pos"], reverse=False))

                    self.reservations.append(pjson)

                    for t in c["tracks"]:
                        track_uri = t["track_uri"]
                        self.current_frequencies[track_uri] -= 1

            if len(self.reservations) >= self.size:
                break

    def _export(self):
        test = dict(playlists=self.reservations[:self.size])
        with open(join(self.out, "test.json"), "w") as o:
            json.dump(test, o, indent=4)

    def generate(self):
        self._count_tracks()
        self._search()
        self._export()
