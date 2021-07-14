from abc import ABC, abstractmethod


class RecEngine(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def recommend(self, p, n):
        pass
