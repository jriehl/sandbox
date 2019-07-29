import nltk
import rdflib

from rdflib.namespace import RDF, RDFS

def walk_tree(graph, branch):
    if isinstance(branch, nltk.Tree):
        result = rdflib.BNode()
        graph.add((result, RDFS.label, rdflib.Literal(branch.label())))
        graph.add((result, RDF.type, RDF.Seq))
        for index, subbranch in enumerate(branch):
            graph.add((result, getattr(RDF, f'{index + 1}'), walk_tree(graph, subbranch)))
    else:
        result = rdflib.Literal(branch)
    return result

def main():
    parser = nltk.parse.CoreNLPParser()
    graph = rdflib.Graph()
    root = list(parser.parse('Welcome to the Ministry of Silly Walks.'.split()))[0]
    rdf_root = walk_tree(graph, root)
    print(graph.serialize(format='turtle').decode())

if __name__ == '__main__':
    main()