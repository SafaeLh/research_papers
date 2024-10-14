import streamlit as st
import pandas as pd
from st_keyup import st_keyup
# from streamlit.type_util import Key
from neo4j import GraphDatabase
from info_search import list_year, df_venue, df_cat, df_key


# Neo4j connection details
NEO4J_URI = "neo4j+s://fa89f20a.databases.neo4j.io"  # Change to your Neo4j URI
NEO4J_USER = "neo4j"  # Change to your Neo4j username
NEO4J_PASSWORD = "m7fDe-K1ntQfJcjrzigJ8g7zKGaKsNO46glDbUSNAgA"  # Change to your Neo4j password


def run_query(uri, user, password, query, params):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run(query, params)
        data = [record.data() for record in result]
    driver.close()
    return data

if 'category_result' not in st.session_state:
    st.session_state.category_result = None
if 'keyword_result' not in st.session_state:
    st.session_state.keyword_result = None


def change_category(df):
    st.session_state.category_result = df_cat[df_cat["categoryName"].str.contains(st.session_state.txt_searchcategory, case=False)]["categoryName"]
    

def change_keyword(df):
    st.session_state.keyword_result = df_key[df_key["keywordName"].str.contains(st.session_state.txt_searchkeyword, case=False)]["keywordName"]

def dataframe_with_selections(df: pd.DataFrame, keys: str="", init_value: bool = False) -> pd.DataFrame:
    df = pd.DataFrame(df)
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", init_value)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
        use_container_width=True,
        height=200,
        key=keys
        
    )
    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)


title_col, empty_col, img_col = st.columns([20, 1, 2])
with title_col:
    st.subheader("Research Papers page")
with img_col:
    st.image("https://dist.neo4j.com/wp-content/uploads/20210423062553/neo4j-social-share-21.png")

title_input = st.text_input("Title", placeholder="Enter a title or a part of it")

col1, col2 = st.columns([2,1])
cat_input = []
key_input = []
with col1:
    with st.container(border=False):
        st.markdown('Categories')
        with st.popover(label='Categories', use_container_width=True):
            st_keyup("Search by category", key='txt_searchcategory',
                         on_change=change_category, args=(df_cat,),
                         placeholder='type to search')
            
            cat_selected = dataframe_with_selections(  st.session_state.category_result, "catt")
            if not cat_selected.empty:
                cat_input = st.multiselect("Selected categories",pd.DataFrame(cat_selected)['categoryName'], pd.DataFrame(cat_selected)['categoryName'])
            

with col1:
    with st.container(border=False):
        st.markdown('Keywords')
        with st.popover(label='Keywords', use_container_width=True):
            st_keyup("Search by keyword", key='txt_searchkeyword',
                on_change=change_keyword, args=(df_key,),
                placeholder='type to search')

            key_selected = dataframe_with_selections(st.session_state.keyword_result, "keyy")
            if not key_selected.empty:
                key_input = st.multiselect("Selected keywords",pd.DataFrame(key_selected)['keywordName'], pd.DataFrame(key_selected)['keywordName'])
    

with col1:
    year_input = st.multiselect(
        "Year of publication",
        list_year, placeholder ='Choose a year')
    

with st.expander("Advanced Filters", expanded=False):
            
            venue_type = st.radio(
                "Type of the Venue",
                ["Journal", "Conference","Workshop","arXiv"],
                index=None,
                horizontal=True
            )
            if venue_type =='Journal':
                 list_venue = df_venue[df_venue['typeName']=='journal']['venueName'].tolist()
            elif venue_type == 'Conference':
                 list_venue = df_venue[df_venue['typeName']=='conference']['venueName'].tolist()
            elif venue_type == 'Workshop':
                 list_venue = df_venue[df_venue['typeName']=='workshop']['venueName'].tolist()
            elif venue_type == 'arXiv':
                 list_venue = df_venue[df_venue['typeName']=='arXiv']['venueName'].tolist()
            else:
                 list_venue = df_venue['venueName'].tolist()


            col1, col2= st.columns([3,1])

            with col1:
                        venue_input = st.selectbox(
                            "Name of the Venue",
                            list(set(list_venue)),
                            index=None, placeholder="Choose a Venue if you want"
                        )

nb_results = st.slider("Number of results", 1, 30,5)

base_query = """
MATCH (p:Paper)
MATCH (p)-[:publishedIn]->(v:Venue)
MATCH (p)-[:hasKeyword]->(k:Keyword)
MATCH (p)-[:belongsTo]->(c:Category)
"""
filters = []
params = {}

if title_input:
    filters.append("toLower(p.title) CONTAINS toLower($title)")
    params['title'] = title_input

if cat_input:
    filters.append("c.categoryName IN $categoryName")
    params['categoryName'] = cat_input

if key_input:
    filters.append("k.keywordName IN $keywords")
    params['keywords'] = key_input

if year_input:
    filters.append("p.yearPublication IN $year")
    params['year'] = year_input

if venue_input:
    filters.append("v.venueName = $venue")
    params['venue'] = venue_input

if filters:
    base_query += " WHERE " + " AND ".join(filters)
    # base_query += "WHERE " + filters[0]

params['limit'] = nb_results

final_query = base_query + " RETURN DISTINCT p.title AS Title, p.url AS URL LIMIT $limit;  "
row, col = 0,0
if st.button('Search', help = 'After a Paper Title search, just click on the button again to redisplay the previous Papers search '):
    if filters:
        results = run_query(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, final_query, params)
        if results:
            df = pd.DataFrame(results)
            # st.dataframe(df, use_container_width=True, hide_index=True)
            st.data_editor(df,use_container_width=True, hide_index=True, column_config={"URL":st.column_config.LinkColumn(
            "URL", display_text="Open Paper"
        )})
      
        else:
            st.write("No results found.")
    else:
         st.write("Apply at least one filter")

paper_title = st.text_input("Paper Details",placeholder = "Copy Title Paper")

paper_query = f"""
    MATCH (p:Paper {{title: '{paper_title}'}})
        MATCH (p)-[:writtenBy]->(a:Author)
        MATCH (p)-[:publishedIn]->(v:Venue)
        MATCH (v)-[:hasType]->(vt:VenueType)
        RETURN p.title AS title,
            collect(DISTINCT a.authorName) AS authors,
            p.yearPublication AS yearPublication,
            p.nbCitations AS nbCitations,
            p.nbPages AS nbPages,
            v.venueName AS venueName,
            v.impactFactor AS impactFactor,
            p.url AS url,
            p.abstract AS abstract;"""

# if st.button("Paper Details"):
paper_result = run_query(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, paper_query,{})
if paper_result:
            col = st.columns([1,5.25])
            col[0].markdown("**Title :**")
            col[1].write(paper_result[0]["title"])

            col[0].markdown("**Authors :**")
            col[1].write(", ".join(paper_result[0]["authors"]))

            col = st.columns(6)
            col[0].markdown("**Year :**")
            col[1].text(paper_result[0]["yearPublication"])
            
            col[2].markdown("**Citations :**")
            col[3].text(int(paper_result[0]["nbCitations"]))
            
            col[4].markdown("**Pages :**")
            col[5].text(paper_result[0]["nbPages"])

            col = st.columns([1,5.25])
            col[0].markdown("**Venue :**")
            col[1].write(paper_result[0]["venueName"])

            col = st.columns([1,5.25])
            col[0].markdown("**URL :**")
            col[1].write(paper_result[0]["url"])

            col[0].markdown("**Abstract :**")
            col[1].write(paper_result[0]["abstract"])

            reference_query = f"""
            MATCH (p:Paper {{title: '{paper_title}'}})-[r]-> (a:Paper)
            RETURN a.title as Title;"""
         
            with st.expander("Paper References", expanded=False):
            
                reference_result = run_query(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, reference_query,{})
                if reference_result:
                    df_ref = pd.DataFrame(reference_result)
                    st.dataframe(df_ref, use_container_width=True, hide_index=True)
                else:
                    st.write("No results found.")
else:
            st.write("No details found for the given Paper.")



     
    


