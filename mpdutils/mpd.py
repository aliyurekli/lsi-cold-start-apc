import json

COLD_START = dict(id=1, seeds=0, lower=10, upper=50, display="Title only")


def read_dataset_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data["playlists"]


def get_pids_from_dataset_json(path):
    playlists = read_dataset_json(path)
    return set([p["pid"] for p in playlists])
