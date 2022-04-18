import gzip
from lxml import etree
import time
import re
import string
import Stemmer
import math
from dataclasses import dataclass
from collections import Counter
import os.path
import requests
from pathlib import Path
path = Path(__file__).parent

data = {'result_ids':[]}

def load_documents():
    start = time.time()
    path = Path(__file__).parent
    with gzip.open(f'{path}/data/enwiki-latest-abstract18.xml.gz', 'rb') as f:
        doc_id = 0
        for _, element in etree.iterparse(f, events=('end',), tag='doc'):
            title = element.findtext('./title')
            url = element.findtext('./url')
            abstract = element.findtext('./abstract')

            yield Abstract(ID=doc_id, title=title, url=url, abstract=abstract)

            doc_id += 1
            element.clear()
    end = time.time()
    print(f'Parsing XML took {end - start} seconds')
    data['parsing_time'] = end - start


# !pip install PyStemmer


# top 25 most common words in English and "wikipedia":
# https://en.wikipedia.org/wiki/Most_common_words_in_English
STOPWORDS = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
                 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
                 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'wikipedia'])
PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))
STEMMER = Stemmer.Stemmer('english')

def tokenize(text):
    return text.split()

def lowercase_filter(tokens):
    return [token.lower() for token in tokens]

def punctuation_filter(tokens):
    return [PUNCTUATION.sub('', token) for token in tokens]

def stopword_filter(tokens):
    return [token for token in tokens if token not in STOPWORDS]

def stem_filter(tokens):
    return STEMMER.stemWords(tokens)

def analyze(text):
    tokens = tokenize(text)
    tokens = lowercase_filter(tokens)
    tokens = punctuation_filter(tokens)
    tokens = stopword_filter(tokens)
    tokens = stem_filter(tokens)

    return [token for token in tokens if token]


def timing(method):
    """
    Quick and dirty decorator to time functions: it will record the time when
    it's calling a function, record the time when it returns and compute the
    difference. There'll be some overhead, so it's not very precise, but'll
    suffice to illustrate the examples in the accompanying blog post.
    @timing
    def snore():
        print('zzzzz')
        time.sleep(5)
    snore()
    zzzzz
    snore took 5.0011749267578125 seconds
    """
    def timed(*args, **kwargs):
        start = time.time()
        result = method(*args, **kwargs)
        end = time.time()

        execution_time = end - start
        data['execution_time'] = execution_time
        if execution_time < 0.001:
            print(f'{method.__name__} took {execution_time*1000} milliseconds')
        else:
            print(f'{method.__name__} took {execution_time} seconds')

        return result
    return timed

class Index:
    def __init__(self):
        self.index = {}
        self.documents = {}

    def index_document(self, document):
        if document.ID not in self.documents:
            self.documents[document.ID] = document
            document.analyze()

        for token in analyze(document.fulltext):
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(document.ID)

    def document_frequency(self, token):
        return len(self.index.get(token, set()))

    def inverse_document_frequency(self, token):
        # Manning, Hinrich and Schütze use log10, so we do too, even though it
        # doesn't really matter which log we use anyway
        # https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html
        frequency = self.document_frequency(token)
        if frequency == 0:
            return 0
        return math.log10(len(self.documents) / self.document_frequency(token))

    def _results(self, analyzed_query):
        return [self.index.get(token, set()) for token in analyzed_query]


    def rank(self, analyzed_query, documents):
        results = []
        if not documents:
            return results
        for document in documents:
            score = 0.0
            for token in analyzed_query:
                tf = document.term_frequency(token)
                idf = self.inverse_document_frequency(token)
                score += tf * idf
            results.append((document, score))
        return sorted(results, key=lambda doc: doc[1], reverse=True)

    @timing
    def search(self, query, search_type='AND', rank=True):
        """
        Still boolean search; this will return documents that contain either all words
        from the query or just one of them, depending on the search_type specified.

        We are still not ranking the results (sets are fast, but unordered).
        """
        if search_type not in ('AND', 'OR'):
            return []
        analyzed_query = analyze(query)
        
        results = self._results(analyzed_query)
        

        if search_type == 'AND':
          # all tokens must be in the document
          documents = [self.documents[doc_id] for doc_id in set.intersection(*results)]
        if search_type == 'OR':
            
          # only one token has to be in the document
            documents = [self.documents[doc_id] for doc_id in set.union(*results)]
        
        if rank:
            return self.rank(analyzed_query, documents)
        return documents

   



@dataclass
class Abstract:
    """Wikipedia abstract"""
    ID: int
    title: str
    abstract: str
    url: str
    term_frequencies = {}
    
    @property
    def fulltext(self):
        return ' '.join([self.title, self.abstract])

    def analyze(self):
        # Counter will create a dictionary counting the unique values in an array:
        # {'london': 12, 'beer': 3, ...}
        self.term_frequencies = Counter(analyze(self.fulltext))

    def term_frequency(self, term):
        return self.term_frequencies.get(term, 0)


#RUNNER

def download_wikipedia_abstracts():
   

    URL = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-abstract18.xml.gz'
    with requests.get(URL, stream=True) as r:
        
        path = Path(__file__).parent

        with open(f'{path}/data/enwiki-latest-abstract18.xml.gz', 'wb') as f:
            # write every 1mb
            for i, chunk in enumerate(r.iter_content(chunk_size=1024*1024)):
                f.write(chunk)
                if i % 10 == 0:
                    data['downloaded_files'] = i
                    print(f'Downloaded {i} megabytes', end='\r')


@timing
def index_documents(documents, index):
    for i, document in enumerate(documents):
        index.index_document(document)
        if i % 5000 == 0:
            data['index_documents'] = i
            print(f'Indexed {i} documents', end='\r')
        if i == 400000:
            break
    return index
if not os.path.exists(f'{path}/data/enwiki-latest-abstract18.xml.gz'):
    download_wikipedia_abstracts()
    
def run_search(search_value):
    index = index_documents(load_documents(), Index())
    data['index_documents'] = len(index.documents)
    print(f'Index contains {len(index.documents)} documents')

    print('Exact Match')
    results = index.search(search_value, search_type='AND', rank=True)
    
    for result in results:
        if result[0].ID not in data['result_ids']:
            data['result_ids'].append(result[0].ID)

            data['results'] = data.get('results', []) + \
                [{'id' : result[0].ID, \
                'title' : result[0].title, \
                'abstract' : result[0].abstract, \
                'url' : result[0].url }] 

            print(f"ID:\t {result[0].ID}")
            print(f"Title:\t {result[0].title}")
            print(f"Abstract:\t {result[0].abstract}")
            print(f"URL:\t {result[0].url}")

    return (data)
