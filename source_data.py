from SPARQLWrapper import SPARQLWrapper, JSON
import random
import sys

# Our SPARQL queries:

workQuery = """
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbc: <http://dbpedia.org/property/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?subject ?object WHERE {
   ?subject rdf:type dbo:Work.
   ?subject dbo:abstract ?object.FILTER(lang(?object) = 'en')

}
LIMIT 15000
"""

personQuery = """
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbc: <http://dbpedia.org/property/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?subject ?object WHERE {
   ?subject rdf:type dbo:Person.
   ?subject dbo:abstract ?object.FILTER(lang(?object) = 'en')

}
LIMIT 15000
"""

animalQuery = """
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbc: <http://dbpedia.org/property/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX umb: <http://umbel.org/umbel/rc/>
    SELECT DISTINCT ?subject ?object WHERE {
       ?subject rdf:type umb:Animal.
       ?subject dbo:abstract ?object.FILTER(lang(?object) = 'en')

    }
    LIMIT 15000
"""



class Query:

    _dbpedia = SPARQLWrapper("http://dbpedia.org/sparql")
    _dbpedia.setReturnFormat(JSON)

    @staticmethod
    def get_results(*args):
        results = ()
        for query in args:
            Query._dbpedia.setQuery(query)
            result = Query._dbpedia.query().convert()
            results = results + (result,)
        return results

    @staticmethod
    def combine_results(*args):
        combination = []
        for result in args:
            combination.extend(result["results"]["bindings"])
        return combination


class SourceData:

    #Processed data elements:
    _resultsWorks, _resultsPersons, _resultsAnimals = Query.get_results(workQuery, personQuery, animalQuery)
    _all_results = Query.combine_results(_resultsWorks, _resultsPersons, _resultsAnimals)
    _data_len = len(_all_results)
    _word_index = None
    _data_examples = None

    def __init__(self):
        SourceData._word_index = SourceData.get_word_index()
        SourceData._data_examples = SourceData.data_examples()

    @staticmethod
    def get_word_index():
        if SourceData._word_index is None:
            print("# Indexing vocabulary words #")
            word_index = {}
            index = 0
            count = 0.0
            for result in SourceData._all_results:
                text = result["object"]["value"]
                text = SourceData._normalize_text(text)
                words = text.split(" ")
                progress(count, SourceData._data_len)
                count = count+1
                for word in words:
                    if word not in word_index:
                        word_index[word] = index
                        index = index+1
            progress(count, SourceData._data_len)
            sys.stdout.write("]\n")
            return word_index
        else:
            return SourceData._word_index

    @staticmethod
    def _normalize_text(text):
        text = text.lower()
        text = text.replace("(", " ").replace(")", " ").replace(", ", " ").replace("; ", " ").replace(". ", " ") \
            .replace("?", " ").replace("!", " ").replace('"', " ").replace("'", " ").replace("<", " ").replace(">", " ") \
            .replace("[", " ").replace("]", " ").replace("{", " ").replace("}", " ")
        return text

    @staticmethod
    def _vectorize_text(normalize_text):
        vector = []
        word_index = SourceData.get_word_index()
        for word in normalize_text:
            if word_index.get(word):
                vector.append(word_index.get(word))
        return vector

    @staticmethod
    def vectorize_text(word_index, text):
        vector = []
        normalize_text = SourceData._normalize_text(text)
        for word in normalize_text:
            if word_index.get(word):
                vector.append(word_index.get(word))
            else:
                vector.append(1)
        return vector

    @staticmethod
    def _randomize_lists_pair(list1, list2):
        list1_copy = list(list1)
        list2_copy = list(list2)
        index = 0
        index_used = []
        for _ in list1:
            random_index = random.randint(0, len(list1) - 1)
            if random_index not in index_used:
                list1_copy[index] = list1[random_index]
                list1_copy[random_index] = list1[index]
                list2_copy[index] = list2[random_index]
                list2_copy[random_index] = list2[index]
                index_used.append(index)
                index_used.append(random_index)
            index = index + 1
        return list1_copy, list2_copy

    @staticmethod
    def data_examples():

        if SourceData._data_examples is None:
            print("# Vectorizing data examples #")
            examples = []
            labels = []
            count = 0
            for result in SourceData._resultsWorks["results"]["bindings"]:
                examples.append(SourceData._vectorize_text(SourceData._normalize_text(result["object"]["value"])))
                labels.append(0)
                progress(count, SourceData._data_len)
                count = count + 1
            for result in SourceData._resultsPersons["results"]["bindings"]:
                examples.append(SourceData._vectorize_text(SourceData._normalize_text(result["object"]["value"])))
                labels.append(1)
                progress(count, SourceData._data_len)
                count = count + 1
            for result in SourceData._resultsAnimals["results"]["bindings"]:
                examples.append(SourceData._vectorize_text(SourceData._normalize_text(result["object"]["value"])))
                labels.append(2)
                progress(count, SourceData._data_len)
                count = count + 1
            progress(count, SourceData._data_len)
            sys.stdout.write("]\n")
            return SourceData._randomize_lists_pair(examples, labels)
        else:
            return SourceData._data_examples


def progress(progress, total):
    ratio = progress/total
    if (ratio*100) % 2 == 0:
        update_progress(ratio)


def update_progress(progress_ratio):
    barLength = 50
    status = ""
    if isinstance(progress_ratio, int):
        progress_ratio = float(progress_ratio)
    if not isinstance(progress_ratio, float):
        progress_ratio = 0
        status = "error: progress var must be float\r\n"
    if progress_ratio < 0:
        progress_ratio = 0
        status = "Halt...\r\n"
    if progress_ratio >= 1:
        progress_ratio = 1
        status = "Done...\r\n"
    block = int(round(barLength * progress_ratio))
    text = "\rPercent: [{0}] {1}% {2}".format("=" * block + "-" * (barLength - block), progress_ratio * 100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

