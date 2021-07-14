import argparse

from testutils import TestGen

CLI = argparse.ArgumentParser()
CLI.add_argument("mpd", help="Absolute path of the mpd data folder")
CLI.add_argument("out", help="Absolute path of the output data folder")
CLI.add_argument("mode", choices=["recsys", "custom"], help="Playlist length limitation mode")
CLI.add_argument("size", type=int, help="Number of playlists to be included")

if __name__ == '__main__':
    args = CLI.parse_args()

    tg = TestGen(mpd=args.mpd, out=args.out, size=args.size, mode=args.mode)
    tg.generate()
