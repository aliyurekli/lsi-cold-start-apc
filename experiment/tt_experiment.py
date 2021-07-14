import mpdutils
import csv

from model import RecEngine


class Experimenter:
    def __init__(self, model, test, n, out):
        self.model: RecEngine = model
        self.test = test
        self.n = n
        self.out = out

    def _export(self, recommendations):
        with open(self.out, "w", newline='') as f:
            writer = csv.writer(f)

            for k, v in recommendations.items():
                for track in v:
                    writer.writerow([k, track])

    def run(self):
        print("Generating recommendations...")
        recommendations = dict()
        playlists = mpdutils.read_dataset_json(self.test)

        cnt = 0
        for p in playlists:
            recs = self.model.recommend(p, self.n)
            recommendations[p["pid"]] = recs
            cnt +=1
            if cnt % 100 == 0:
                print(cnt)

        self._export(recommendations)
        print("Recommendations are produced %s" % self.out)
