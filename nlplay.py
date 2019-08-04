import nltk
import rdflib

from rdflib.namespace import RDF, RDFS

def tree_to_rdf(graph, branch):
    'Recursively translate from a NLTK tree into a RDF graph.'
    if isinstance(branch, nltk.Tree):
        result = rdflib.BNode()
        graph.add((result, RDFS.label, rdflib.Literal(branch.label())))
        graph.add((result, RDF.type, RDF.Seq))
        for index, subbranch in enumerate(branch):
            graph.add((result, RDF[index + 1], tree_to_rdf(graph, subbranch)))
    else:
        result = rdflib.Literal(branch)
    return result

def rdf_to_tree(graph, root):
    'Recursively translate from a RDF tree to a NLTK tree.'
    if isinstance(root, rdflib.Literal):
        result = root.value
    else:
        labels = list(graph[root:RDFS.label])
        label = labels[0].value if labels else None
        seq = graph.seq(root)
        if seq is None:
            children = []
        else:
            children = [rdf_to_tree(graph, child) for child in seq]
        result = nltk.Tree(label, children)
    return result

def get_roots(graph):
    'Find all parse tree root nodes in the given graph.'
    return list(graph[:RDFS.label:rdflib.Literal('ROOT')])

def main():
    parser = nltk.parse.CoreNLPParser()
    graph = rdflib.Graph()
    root = list(parser.parse('Welcome to the Ministry of Silly Walks.'.split()))[0]
    rdf_root = tree_to_rdf(graph, root)
    print(graph.serialize(format='turtle').decode())
    root_2 = rdf_to_tree(graph, rdf_root)
    assert root == root_2
    root_2.pretty_print()
    return graph, root_2

if __name__ == '__main__':
    main()
