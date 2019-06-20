from SPARQLWrapper import SPARQLWrapper, JSON
import random


sparql = SPARQLWrapper("http://dbpedia.org/sparql")

personQuery = """
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbc: <http://dbpedia.org/property/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?subject ?object WHERE {
   ?subject rdf:type dbo:Person.
   ?subject dbo:abstract ?object.FILTER(lang(?object) = 'en')
   
}
LIMIT 1000
"""

workQuery = """
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbc: <http://dbpedia.org/property/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?subject ?object WHERE {
   ?subject rdf:type dbo:Work.
   ?subject dbo:abstract ?object.FILTER(lang(?object) = 'en')
   
}
LIMIT 1000
"""
sparql.setQuery(workQuery)
sparql.setReturnFormat(JSON)
resultsWorks = sparql.query().convert()
sparql.setQuery(personQuery)
resultsPersons = sparql.query().convert()
counter = 0

all_results = resultsWorks["results"]["bindings"][:]
all_results.extend(resultsPersons["results"]["bindings"])
print(len(all_results))

def normalize_text(text):
    text = text.lower()
    text = text.replace("(", " ").replace(")", " ").replace(", ", " ").replace("; ", " ").replace(". ", " ")\
        .replace("?", " ").replace("!", " ").replace('"', " ").replace("'", " ").replace("<", " ").replace(">", " ")\
        .replace("[", " ").replace("]", " ").replace("{", " ").replace("}", " ")
    return text
def to_index(normalize_text):
    vector = []
    word_index = get_word_index()
    for word in normalize_text:
        if word_index.get(word):
            vector.append(word_index.get(word))
    return vector
def randomize_lists(list1, list2):
    list1_copy = list(list1)
    list2_copy = list(list2)
    index = 0
    index_uses=[]
    for element in list1:
        random_index = random.randint(0, len(list1)-1)
        if random_index not in index_uses:
            list1_copy[index] = list1[random_index]
            list1_copy[random_index] = list1[index]
            list2_copy[index] = list2[random_index]
            list2_copy[random_index] = list2[index]
            index_uses.append(index)
            index_uses.append(random_index)
        index=index+1
    return list1_copy, list2_copy

def data_examples():
    examples=[]
    labels=[]
    for result in resultsWorks["results"]["bindings"]:
        examples.append(to_index(normalize_text(result["object"]["value"])))
        labels.append(0)
    for result in resultsPersons["results"]["bindings"]:
        examples.append(to_index(normalize_text(result["object"]["value"])))
        labels.append(1)
    return randomize_lists(examples, labels)

def word_occurrence():
    occurrencesDict = {}
    for result in all_results:
        text = result["object"]["value"]
        text = normalize_text(text)
        words = text.split(" ")
        for word in words:
            if word in occurrencesDict:
                occurrencesDict[word] = occurrencesDict[word]+1
            else:
                new = {word: 1}
                occurrencesDict.update(new)
    return sorted(occurrencesDict.items(), key=lambda item: item[1], reverse=True)

def get_word_index():
    sortedWordByOcurrence = word_occurrence()
    word_index={}
    counter = 0
    for pair in sortedWordByOcurrence:
        word = pair[0]
        new_pair = {word: counter}
        word_index.update(new_pair)
        counter = counter+1
    return word_index

