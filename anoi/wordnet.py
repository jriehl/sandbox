from typing import Dict, Iterable

from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Lemma, Synset
import tqdm

from . import anoi


NIL = anoi.ANOIReserved.NIL.value


class ANOIWordNetLoader:
    lemma_uid: int = NIL
    synset_uid: int = NIL
    definition_uid: int = NIL
    antonym_uid: int = NIL
    hypernym_uid: int = NIL
    hyponym_uid: int = NIL

    def __init__(self, namespace: anoi.ANOINamespace, verbose: bool = False):
        self.space = namespace.space
        self.namespace = namespace
        self.ns_proxy = anoi.ANOITrieProxy(namespace)
        self.term_map: Dict[str, int] = {}
        self.lemma_map: Dict[Lemma, int] = {}
        self.synset_map: Dict[Synset, int] = {}
        self.verbose: bool = verbose
        self.loaded = self.init_wordnet_props()

    def init_wordnet_props(self):
        loaded = True
        for uid_prop in self.__annotations__:
            wordnet_term = uid_prop[:-4]
            prop_uid = self.namespace.get_name(wordnet_term)
            if prop_uid == NIL:
                loaded = False
                break
            setattr(self, uid_prop, prop_uid)
        return loaded

    def build_vec(self, vec_uids: Iterable[int]) -> int:
        result = self.space.get_uid()
        self.space.set_content(result, tuple(vec_uids))
        return result

    def define_everything(self):
        synset_iter = wn.all_synsets()
        if self.verbose:
            synset_iter = tqdm.tqdm(list(synset_iter), 'define_synsets')
        for synset in synset_iter:
            self.define_synset(synset)
        all_lemma_names = set.union(
            *(set(ss.lemma_names()) for ss in wn.all_synsets()))
        all_lemmas = set.union(*(set(ss.lemmas()) for ss in wn.all_synsets()))
        assert len(all_lemma_names) == len(all_lemmas)
        for lemma_name in (
                tqdm.tqdm(all_lemma_names, 'define_terms')
                if self.verbose else all_lemma_names):
            self.define_term(lemma_name.replace('_', ' '))
        self.definition_uid = self.term_map['definition']
        for lemma in (
                tqdm.tqdm(all_lemmas, 'define_lemmas')
                if self.verbose else all_lemmas):
            self.define_lemma(lemma)

    def define_lemma(self, lemma: Lemma) -> int:
        lemma_uid = self.lemma_map.get(lemma)
        if lemma_uid is None:
            # TODO: Could we check for a lemma's definition somehow?
            lemma_uid = self.space.get_uid()
            self.lemma_map[lemma] = lemma_uid
        return lemma_uid

    def define_synset(self, synset: Synset) -> int:
        synset_uid = self.synset_map.get(synset)
        if synset_uid is None:
            # TODO: Is there some means to check for a synset's existence in a
            # space?  Could there be?
            synset_uid = self.space.get_uid()
            self.synset_map[synset] = synset_uid
        return synset_uid

    def define_term(self, term: str) -> int:
        term_uid = self.term_map.get(term)
        if term_uid is not None:
            assert self.namespace.get_name(term) == term_uid
        else:
            ns_uid = self.ns_proxy[term]
            if ns_uid == NIL:
                term_uid = self.space.get_uid()
                self.term_map[term] = term_uid
                self.namespace.set_name(term, term_uid)
            else:
                self.term_map[term] = term_uid = ns_uid
        return term_uid

    def load(self):
        self.define_everything()
        if not self.init_wordnet_props():
            raise RuntimeError(
                'failed to initialize common properties after defining all '
                'terms in WordNet')
        self.load_terms()
        self.load_lemmas()
        self.load_synsets()
        if self.verbose:
            self.report()
        self.loaded = True

    def load_lemmas(self):
        map_iter = self.lemma_map.items()
        if self.verbose:
            map_iter = tqdm.tqdm(map_iter, desc='load_lemmas()')
        lemma_prop = self.term_map['lemma']
        for lemma, lemma_uid in map_iter:
            lemma_name = lemma.name()
            term_candidate = lemma_name.replace('_', ' ')
            if term_candidate in self.term_map:
                name_uid = self.space.cross(
                    self.term_map[term_candidate], self.namespace.NAME)
                assert name_uid != NIL
                self.space.cross_equals(
                    lemma_uid, self.namespace.NAME, name_uid)
            else:
                self.namespace.name_atom(lemma_uid, term_candidate)
            self.space.cross_equals(
                lemma_uid, self.synset_uid, self.synset_map[lemma.synset()])
            antonyms = lemma.antonyms()
            if len(antonyms) > 0:
                self.space.cross_equals(
                    lemma_uid, self.antonym_uid, self.build_vec(
                        self.lemma_map[antonym] for antonym in antonyms))
            self.space.cross_equals(lemma_uid, self.namespace.TYPE, lemma_prop)

    def load_synsets(self):
        map_iter = self.synset_map.items()
        if self.verbose:
            map_iter = tqdm.tqdm(map_iter, desc='load_synsets()')
        synset_prop = self.term_map['synset']
        for synset, synset_uid in map_iter:
            hypernyms = synset.hypernyms()
            if len(hypernyms) > 0:
                self.space.cross_equals(
                    synset_uid, self.hypernym_uid, self.build_vec(
                        self.synset_map[hypernym] for hypernym in hypernyms
                    )
                )
            hyponyms = synset.hyponyms()
            if len(hyponyms) > 0:
                self.space.cross_equals(
                    synset_uid, self.hyponym_uid, self.build_vec(
                        self.synset_map[hyponym] for hyponym in hyponyms))
            definition_atom = self.build_vec(
                anoi.compress_iter(
                    self.namespace, anoi.str_to_vec(synset.definition())))
            self.space.cross_equals(
                synset_uid, self.definition_uid, definition_atom)
            self.space.cross_equals(
                definition_atom, self.namespace.TYPE, self.definition_uid)
            self.space.cross_equals(
                synset_uid, self.namespace.TYPE, synset_prop)

    def load_terms(self):
        map_iter = self.term_map.items()
        if self.verbose:
            map_iter = tqdm.tqdm(map_iter, desc='load_terms()')

        for term, term_uid in map_iter:
            lemma_name = term.replace(' ', '_')
            # Link lemmas
            lemmas_uid = self.build_vec(
                self.lemma_map[lemma] for lemma in wn.lemmas(lemma_name))
            self.space.cross_equals(term_uid, self.lemma_uid, lemmas_uid)
            # Link synsets
            synsets_uid = self.build_vec(
                self.synset_map[synset] for synset in wn.synsets(lemma_name))
            self.space.cross_equals(term_uid, self.synset_uid, synsets_uid)

    def report(self):
        characters = 0
        uids = 0
        for synset, synset_uid in self.synset_map.items():
            characters += len(synset.definition())
            uids += len(self.space.get_content(
                self.space.cross(synset_uid, self.definition_uid)))
        print(f'Total definitions in code points: {characters}')
        print(f'Total definitions in UIDs: {uids}')
        print(f'Compression ratio: 1:{characters/uids}')
        if hasattr(self.space, 'uid_map'):
            print(f'Allocated atom count: {len(self.space.uid_map)}')


def main():
    space = anoi.ANOIInMemorySpace()
    namespace = anoi.ANOINamespace(space, 'wordnet')
    loader = ANOIWordNetLoader(namespace, True)
    loader.load()


if __name__ == '__main__':
    main()
