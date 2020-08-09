'''Playing with a re-write of Spacy's named entity linking project.
'''
import bz2
from concurrent.futures import Executor, ThreadPoolExecutor
import io
import itertools
import multiprocessing
import re
import sys

from lxml import etree

import numpy as np
import pandas as pd

import dask.distributed as dd
import dask.bag as db

link_regex = re.compile(r"\[\[[^\[\]]*\]\]") # Regex borrowed from Spacy project.

XML_NS = '{http://www.mediawiki.org/xml/export-0.10/}'

def get_tag(postfix):
    return f'{XML_NS}{postfix}'

def page_iter(fileobj: io.IOBase):
    for _, element in etree.iterparse(fileobj, tag=get_tag('page')):
        yield element

def text_iter(fileobj: io.IOBase):
    for page in page_iter(fileobj):
        for text in page.itertext(with_tail=False):
            yield text

def page_reducer(accumulator, page):
    return handle_page(page, accumulator)

def entity_count_reducer(acc: dict, crnt: dict):
    acc = acc.copy()
    for key, value in crnt.items():
        if key not in acc:
            acc[key] = value
        else:
            acc[key] += value
    return acc

def handle_page(page, accumulator: dict = None):
    if accumulator is None:
        result = {}
    else:
        result = accumulator
    for child_text in page.itertext(with_tail=False):
        for link in link_regex.findall(child_text):
            if link not in result:
                result[link] = 0
            result[link] += 1
    return result

def handle_page_text(page_text):
    result = {}
    for link in link_regex.findall(page_text):
        if link not in result:
            result[link] = 0
        result[link] += 1
    return pd.Series(result, dtype=np.int64)

def fold_pd_series(series0 : pd.Series, series1 : pd.Series):
    return series0.combine(series1, np.add, fill_value=0)

def build_mr_job(fileobj: io.IOBase):
    return (db.from_sequence(text_iter(fileobj))
              .map(handle_page_text)
              .filter(lambda series: len(series) > 0)
              .fold(fold_pd_series))

def page_list_iter(fileobj: io.IOBase, list_size=100):
    pages = page_iter(fileobj)
    while True:
        yield list(itertools.islice(pages, list_size))

def handle_pages(pages):
    result = {}
    for page in pages:
        #crnt_id = page.find(get_tag('id')).text
        handle_page(page, result)
    return result

def pretrain_kb(wikipedia_dump_path, executor: Executor, verbose=False):
    # XXX: Attempting to partition a BZ2 XML file by articles.
    with bz2.open(wikipedia_dump_path, 'rb') as wikipedia_dump_file:
        for pages in page_list_iter(wikipedia_dump_file):
            if verbose:
                # Show progress through the dump file.
                print(f'Processed or buffered {wikipedia_dump_file.tell()} '
                      'bytes. Last page id was:', pages[-1].find(f'{XML_NS}id').text)
            pages_future = executor.submit(handle_pages, pages)

def main():
    args = list(sys.argv[1:])
    verbose = False
    if '-v' in args:
        args.remove('-v')
        verbose = True
    client = dd.Client()
    print(client.dashboard_link)
    for filepath in args:
        with bz2.open(filepath, 'rb') as wikipedia_dump_file:
            job = build_mr_job(wikipedia_dump_file)
            freqs = job.compute()
        #pretrain_kb(filepath, executor, verbose)

if __name__ == '__main__':
    main()
