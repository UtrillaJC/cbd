from SPARQLWrapper import SPARQLWrapper, JSON

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
LIMIT 15000
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
LIMIT 15000
"""
sparql.setQuery(personQuery)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
counter = 0
for result in results["results"]["bindings"]:
    print(result["subject"]["value"])
    counter = counter+1
print(counter)