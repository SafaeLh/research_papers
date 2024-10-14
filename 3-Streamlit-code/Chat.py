import streamlit as st
from langchain_openai import OpenAI
# from langchain.graphs import Neo4jGraph
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate
from training import examples, schema_ttl


# Neo4j connection details
NEO4J_URI = "your URI"  # Change to your Neo4j URI
NEO4J_USER = "neo4j"  # Change to your Neo4j username
NEO4J_PASSWORD = "your password"  # Change to your Neo4j password


cypher_generation_template = f"""
You are an expert Neo4j Cypher translator who converts English to Cypher based on the Neo4j Schema provided, following the instructions below:
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
schema:
{schema_ttl}

Examples:
{examples}

Question: {{question}}
"""
cypher_prompt = PromptTemplate(
    template = cypher_generation_template,
    input_variables = ["question"]
)

CYPHER_QA_TEMPLATE = """You are an assistant of an advanced retrieval augmented system, who prioritizes accuracy and is very context-aware.
                 Pleass summarize text from the following and generate a comprehensive, logical and context_aware answer.
The information part contains the provided information that you must use to construct an answer.
The provided information is authoritative, you must never doubt it or try to use your internal knowledge to correct it.
if the user asks you to process the data retrieved from the graph, you can do so. For example, if he asks you to give him the main algorithms or methods used in a paper based on his text, you retrieve the text from the graph and then answer him.
Make the answer sound as a response to the question. Do not mention that you based the result on the given information.
Each time you receive a response from the cypher query form nice and human understandable answers and return it. if not return what is in the database
If the provided information is empty, just answer by yourself
Final answer should be easily readable and structured.

Information:
{context}

Question: {question}
Helpful Answer:"""

qa_prompt = PromptTemplate(
    input_variables=["context", "question"], template=CYPHER_QA_TEMPLATE
)

def query_graph(user_input,openAi_key):
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)
    # graph = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    chain = GraphCypherQAChain.from_llm(
        llm=OpenAI(api_key=openAi_key,temperature=0.5),
        graph=graph,
        return_intermediate_steps=True,
        cypher_prompt=cypher_prompt,
        qa_prompt=qa_prompt,
        allow_dangerous_requests=True
        )
    result = chain(user_input)
    return result


st.set_page_config(layout="wide")

title_col, empty_col, img_col = st.columns([20, 1, 2])    

with title_col:
    st.subheader("Research Papers Assistant")
with img_col:
    st.image("https://dist.neo4j.com/wp-content/uploads/20210423062553/neo4j-social-share-21.png")


with st.sidebar:
    st.markdown("If you have an OpenAI key let's CHAT !")
    openAi_key = st.text_input("OpenAI API Key", key="langchain_search_api_key_openai", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

    st.markdown(" ")
    st.markdown("If not let's SEARCH !")
    if st.button("Search Page"):
        st.switch_page("pages/Search.py")

    st.markdown(" ")
    st.markdown("OR let me recommend you some")
    if st.button("Recommender Paper"):
        st.switch_page("pages/Recommender.py")
    st.caption("Coming soon ...")

    "[More info (Github)](https://github.com/SafaeLh/research_papers.git)"



msg_col, graph_col = st.columns([1.5, 1])

# Chat interface
messages = msg_col.container(height=425, border=False)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi there, ask me a question."}]

for msg in st.session_state.messages:
    messages.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask a question about AI or ML Papers")
cypher_query = ""
database_results = ""

if user_input:
    with st.spinner("Processing your question..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        messages.chat_message("user").write(user_input)
        if openAi_key:
         try:
            result = query_graph(user_input,openAi_key)
            
            intermediate_steps = result["intermediate_steps"]
            cypher_query = intermediate_steps[0]["query"]
            database_results = intermediate_steps[1]["context"]

            answer = result["result"]
            st.session_state.messages.append({"role": "assistant", "content": answer})
            messages.chat_message("assistant").write(answer)

         except Exception as e:
            messages.write("Failed to process question. Please try again.")
            print(e)
        else:
            messages.error("Please add your OpenAI API key to continue.")


# Details interface

tab_container = graph_col.container()

if tab_container.checkbox("Show details",value=True):
    tab1, tab2 = tab_container.tabs(["Cipher", "Database"])

    with tab1:
        if cypher_query:
            st.text_area("Last Cypher Query", cypher_query, key="_cypher", height=300)

    with tab2:
        
        if database_results:
            st.text_area("Last Database Results", database_results, key="_database", height=300)
        




