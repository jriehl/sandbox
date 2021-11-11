from typing import Dict, Iterable
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Lemma, Synset

import anoi


NIL = anoi.ANOIReserved.NIL.value


class ANOIWordNetLoader:
    def __init__(self, namespace: anoi.ANOINamespace):
        self.space = namespace.space
        self.namespace = namespace
        self.ns_proxy = anoi.ANOITrieProxy(namespace)
        self.term_map: Dict[str, int] = {}
        self.lemma_map: Dict[Lemma, int] = {}
        self.synset_map: Dict[Synset, int] = {}

    def build_set(self, set_uids: Iterable[int]) -> int:
        result = self.space.get_uid()
        self.space.set_content(result, tuple(set_uids))
        return result

    def define_everything(self):
        for synset in wn.all_synsets():
            self.define_synset(synset)
        all_lemma_names = set.union(
            *(set(ss.lemma_names()) for ss in wn.all_synsets()))
        all_lemmas = set.union(*(set(ss.lemmas()) for ss in wn.all_synsets()))
        assert len(all_lemma_names) == len(all_lemmas)
        for lemma_name in all_lemma_names:
            self.define_term(lemma_name.replace('_', ' '))
        for lemma in all_lemmas:
            self.define_lemma(lemma)

    def define_lemma(self, lemma: Lemma) -> int:
        lemma_uid = self.lemma_map.get(lemma)
        if lemma_uid is None:
            lemma_uid = self.space.get_uid()
            self.lemma_map[lemma] = lemma_uid
            self.space.set_content(lemma_uid, anoi.str_to_vec(lemma.name()))
        return lemma_uid

    def define_synset(self, synset: Synset) -> int:
        synset_uid = self.synset_map.get(synset)
        if synset_uid is None:
            synset_uid = self.space.get_uid()
            self.synset_map[synset] = synset_uid
        return synset_uid

    def define_term(self, term: str) -> int:
        term_uid = self.term_map.get(term)
        if term_uid is not None:
            assert self.namespace.get_name(term) == term_uid
        else:
            term_uid = self.space.get_uid()
            self.term_map[term] = term_uid
            self.space.set_content(term_uid, anoi.str_to_vec(term))
            assert self.namespace.get_name(term) == NIL
            self.namespace.set_name(term, term_uid)
        return term_uid

    def load(self):
        self.define_everything()
        lemma_uid = self.namespace.get_name('lemma')
        synset_uid = self.namespace.get_name('synset')
        assert lemma_uid != NIL and synset_uid != NIL
        for term, term_uid in self.term_map.items():
            lemma_name = term.replace(' ', '_')
            # Link lemmas
            lemmas_uid = self.build_set(
                self.lemma_map[lemma] for lemma in wn.lemmas(lemma_name))
            self.space.cross_equals(term_uid, lemma_uid, lemmas_uid)
            # Link synsets
            synsets_uid = self.build_set(
                self.synset_map[synset] for synset in wn.synsets(lemma_name))
            self.space.cross_equals(term_uid, synset_uid, synsets_uid)
        # for synset in self.synset_map.keys():
        #     self.load_synset(synset)
        # for lemma in self.lemma_map.keys():
        #     self.load_lemma(lemma)

    def load_lemma(self, lemma: Lemma):
        raise NotImplementedError()

    def load_synset(self, synset: Synset):
        raise NotImplementedError()


def main():
    space = anoi.ANOIInMemorySpace()
    namespace = anoi.ANOINamespace(space, 'wordnet')
    loader = ANOIWordNetLoader(namespace)
    loader.load()


if __name__ == '__main__':
    main()
