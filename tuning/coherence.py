from model import SerializationReader

from gensim.corpora import Dictionary
from gensim.models import LsiModel
from gensim.models.coherencemodel import CoherenceModel


class CoherenceEstimator:
    def __init__(self, series):

        print("Reading serializations...")
        sr = SerializationReader(series=series)
        documents, doc2idx, idx2doc = sr.read()

        print("Building dictionary...")
        self.dictionary = Dictionary(documents)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in documents]

    def estimate(self, dimension):
        lsi = LsiModel(corpus=self.corpus, id2word=self.dictionary, num_topics=dimension)
        coherence = CoherenceModel(model=lsi, corpus=self.corpus, dictionary=self.dictionary, coherence="u_mass")

        return coherence.get_coherence()
