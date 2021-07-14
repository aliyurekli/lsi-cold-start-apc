import re
import csv


def normalize(name):
    name = name.lower()
    name = re.sub(r"[.,/#!$%^*;:{}=_`~()@]", ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


class LookupNormalization:
    def __init__(self):
        self.__lookup = {}

        with open("./auxy/lookup.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                self.__lookup[row[0]] = row[1]

    def lookup(self, name):
        standard = normalize(name)
        return self.__lookup[standard]
