import pandas as pd
from neo4j import GraphDatabase

# Neo4j connection details
NEO4J_URI = "neo4j+s://fa89f20a.databases.neo4j.io"  # Change to your Neo4j URI
NEO4J_USER = "neo4j"  # Change to your Neo4j username
NEO4J_PASSWORD = "m7fDe-K1ntQfJcjrzigJ8g7zKGaKsNO46glDbUSNAgA"  # Change to your Neo4j password

# Connect to Neo4j
# graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
graph = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


queries = {
    "categoryName": "MATCH (c:Category) RETURN DISTINCT c.categoryName AS categoryName",
    "keywordName": "MATCH (k:Keyword) RETURN DISTINCT k.keywordName AS keywordName",
    "yearPublication": "MATCH (p:Paper) RETURN DISTINCT p.yearPublication AS yearPublication",
    # "venueName": "MATCH (v:Venue) RETURN DISTINCT v.venueName AS venueName"
}

venue_query =  """
MATCH (v:Venue)-[:hasType]->(vt:VenueType)
RETURN DISTINCT v.venueName AS venueName, v.impactFactor AS impactFactor, vt.typeName AS typeName
"""

def run_query(driver, query):
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]

results = {key: run_query(graph, query) for key, query in queries.items()}
dfs = {key: pd.DataFrame(result) for key, result in results.items()}
df_year = dfs["yearPublication"]
list_year = df_year[~df_year["yearPublication"].isna()]["yearPublication"].astype('int').tolist()
df_cat = dfs['categoryName']
df_key = dfs['keywordName']

venue_result = run_query(graph, venue_query)
df_venue = pd.DataFrame(venue_result)
df_venue['impactFactor'] = df_venue['impactFactor'].astype('float')

graph.close()