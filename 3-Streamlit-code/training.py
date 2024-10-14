instructions = """
1. Generate Cypher query compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE, HAVING keywords in the cypher. Use alias when using the WITH keyword
3. Use only Nodes and relationships mentioned in the schema
4. Always do a case-insensitive and fuzzy search for any properties related search. Eg: to search for an Author, use `toLower(Author.authorName) contains 'neo4j'`. To search for title, use 'toLower(Paper.title) contains 'neo4j'`. To search for a project, use `toLower(Paper.title) contains 'knowledge graph' OR toLower(Paper.abstract) contains 'knowledge graph'`.)
5. Never use relationships that are not mentioned in the given schema
6. When asked about a ppaer, Match the properties using case-insensitive matching and the OR-operator, E.g, to find a knowledge graph paper, use `toLower(Paper.title) contains 'knowledge graph' OR toLower(Paper.abstract) contains 'knowledge graph'`.
7. if not specified limit the number of answer to 10
8. Don't accept any update in the database using Cypher statement, if a user ask to update or change something in the graph, kindly refuse.
9. if the user uses acronyms or abbreviations like "kg" try to find the whole expression, (kg=knowledge graph) then use it in the cypher
10. when you have a response, never start your answer by Unfortunately
11. when asked about a paper and its authors, don't forget that the relationship is ALWAYS from Paper to Author. Eg (p:Paper)-[:writtenBy]->(a:Author); (a:Author)<-[:writtenBy]-(p:Paper)
12. last, if you fail to generate the cypher expression just answer by yourself
"""
instructions_qa = """
Pleass summarize text from the following and generate a comprehensive, logical and context_aware answer.
The information part contains the provided information that you must use to construct an answer.
The provided information is authoritative, you must never doubt it or try to use your internal knowledge to correct it.
if the user asks you to process the data retrieved from the graph, you can do so. For example, if he asks you to give him the main algorithms or methods used in a paper based on his text, you retrieve the text from the graph and then answer him.
Make the answer sound as a response to the question. Do not mention that you based the result on the given information.
Each time you receive a response from the cypher query form nice and human understandable answers and return it. if not return what is in the database
If the provided information is empty, just answer by yourself
Final answer should be easily readable and structured.
"""
examples = """
Question: Which papers have the most citations ? 
Answer: ``` 
MATCH (p:Paper)
WHERE p.nbCitations IS NOT NULL AND p.nbCitations < 10000
RETURN p.title AS title, p.nbCitations AS nbCitations, p.url AS url
ORDER BY p.nbCitations DESC
LIMIT 10;
```
Question: who wrote the most papers?
Answer: ```
MATCH (a:Author)<-[:writtenBy]-(p:Paper)
RETURN a.authorName AS author, COUNT(p) AS paperCount
ORDER BY paperCount DESC
LIMIT 10;
```
Question: I want the papers that deal with knowledge graphs
Answer: ```
MATCH (p:Paper)
WHERE toLower(p.title) CONTAINS 'knowledge graph' OR toLower(p.abstract) CONTAINS 'knowledge graph'
RETURN p.title AS title, p.url as url
LIMIT 10;
```
Question: in which year this paper was published "A Comprehensive Survey on Automatic Knowledge Graph Construction"
Answer: ```
MATCH (p:Paper)
WHERE toLower(p.title) CONTAINS 'a comprehensive survey on automatic knowledge graph construction'
RETURN p.yearPublication AS yearPublication
LIMIT 1;
```
Question: and who wrote it?
Answer: ```
MATCH (p:Paper)-[:writtenBy]->(a:Author)
WHERE toLower(p.title) CONTAINS 'a comprehensive survey on automatic knowledge graph construction'
RETURN collect(a.authorName) AS authors
LIMIT 1;
```
Question: give me the summary/abstract??
Answer: ```
MATCH (p:Paper)
WHERE toLower(p.title) CONTAINS 'a comprehensive survey on automatic knowledge graph construction'
RETURN p.abstract AS abstract
LIMIT 1;
```
Question: in which venue are the most papers published and what is its type 
Answer: ```
MATCH (p:Paper)-[:publishedIn]->(v:Venue)-[:hasType]->(vt:VenueType)
RETURN v.venueName AS venue, vt.typeName AS type, COUNT(p) AS paperCount
ORDER BY paperCount DESC
LIMIT 5
```
Question: in which category can I find papers dealing with knowledge graphs embedding?
Answer: ```
MATCH (p:Paper)-[:belongsTo]->(c:Category)
WHERE toLower(p.title) CONTAINS 'knowledge graph embedding' OR toLower(p.abstract) CONTAINS 'knowledge graph embedding'
WITH c, count(p) AS numberOfPapers
RETURN c.categoryName AS categoryName
ORDER BY numberOfPapers DESC
LIMIT 10
```
Question: do you have access to the full text of 'ProjE: Embedding Projection for Knowledge Graph Completion'? give me the takeaway ideas and the methods and algorithms that they used?
Answer: ```
MATCH (p:Paper)
WHERE toLower(p.title) CONTAINS 'proje: embedding projection for knowledge graph completion'
RETURN p.fullText AS fullText
LIMIT 1
```
Question: i want 5 papers submitted between 2020 and 2024 with a number of citation higher that 50 and were submitted to AAAI and deal with KG embedding
Answer: ```
MATCH (p:Paper)-[:publishedIn]->(v:Venue)
WHERE p.nbCitations > 50 
AND p.yearPublication >= 2020 
AND p.yearPublication <= 2024 
AND toLower(v.venueName) CONTAINS 'aaai'
AND (toLower(p.title) CONTAINS 'knowledge graph embedding' OR toLower(p.abstract) CONTAINS 'knowledge graph embedding')
RETURN p.title AS title, p.yearPublication AS year, p.nbCitations AS citations, p.abstract AS abstract
LIMIT 5
```
"""

schema_ttl = """
##Class Definitions with their Data type propreties (Number of Classes 6)  ###
:Paper rdf:type owl:Class; 
    :paperID rdf:type owl:DatatypeProperty ;
    :title rdf:type owl:DatatypeProperty ;
    :DOI rdf:type owl:DatatypeProperty ;
    :fullText rdf:type owl:DatatypeProperty ;
    :nbCitations rdf:type owl:DatatypeProperty ;
    :dateSubmission rdf:type owl:DatatypeProperty ;
    :yearPublication rdf:type owl:DatatypeProperty ;
    :abstract rdf:type owl:DatatypeProperty ;
    :url rdf:type owl:DatatypeProperty ;
    :nbPages rdf:type owl:DatatypeProperty ;
    
:Venue rdf:type owl:Class; 
    :venueID rdf:type owl:DatatypeProperty ;
    :venueName rdf:type owl:DatatypeProperty ;
    :impactFactor rdf:type owl:DatatypeProperty ;
:Author rdf:type owl:Class; 
    :authorID rdf:type owl:DatatypeProperty ;
    :authorName rdf:type owl:DatatypeProperty ;
    :authorAffiliation rdf:type owl:DatatypeProperty ;
:Keyword rdf:type owl:Class; 
    :keywordID rdf:type owl:DatatypeProperty ;
    :keywordName rdf:type owl:DatatypeProperty ;
:Category rdf:type owl:Class; 
    :categoryID rdf:type owl:DatatypeProperty ;
    :categoryName rdf:type owl:DatatypeProperty ;
    :categoryDescription rdf:type owl:DatatypeProperty ;
:VenueType rdf:type owl:Class; 
    :typeName rdf:type owl:DatatypeProperty ;

###  Relationship Definitions (Number of relationships) 6 ###
:publishedIn rdf:type owl:ObjectProperty ;
             rdfs:domain :Paper;
             rdfs:range :Venue . 
:cites rdf:type owl:ObjectProperty ;
       rdfs:domain :Paper;
       rdfs:range :Paper . 
:hasKeyword rdf:type owl:ObjectProperty ;
            rdfs:domain :Paper;
            rdfs:range :Keyword . 
:writtenBy rdf:type owl:ObjectProperty ;
           rdfs:domain :Paper;
           rdfs:range :Author . 
:belongsTo rdf:type owl:ObjectProperty ;
           rdfs:domain :Paper;
           rdfs:range :Category . 
:hasType rdf:type owl:ObjectProperty ;
         rdfs:domain :Venue;
         rdfs:range :VenueType .
"""