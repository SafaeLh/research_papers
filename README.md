# Knowledge Graph Construction for AI Academic Research Papers with Neo4j and Streamlit

This project focuses on constructing a Knowledge Graph (KG) of academic research papers related to various advanced topics, such as Knowledge Graphs, Natural Language Processing, Graph Neural Networks, Attention Networks, Contrastive Learning, Transformers, Generative Adversarial Nets, Computer Vision, Artificial Intelligence, and Knowledge Graph Embedding. The data encompasses papers published up to early 2024.

The construction is done by fetching, cleaning, and structuring data from various sources, including ArXiv, Google Scholar, and full-text papers. The KG is built and populated using Neo4j, and the data is made accessible via a Streamlit app with a chatbox powered by OpenAI.
<div align="center">
    <img width="346" alt="image" src="https://github.com/user-attachments/assets/e19c7618-3c91-43f9-a9a0-946c4f63b195">
</div>



## Features
- **Data Collection**: Fetches data from ArXiv, Google Scholar, and full-text papers, extracting relevant information such as titles, authors, keywords, venues, and citations.
  
- **Data Cleaning and Preparation**: Cleans and structures data into formats suitable for KG construction, including entity and relationship dataframes.
  
- **Knowledge Graph Construction**: 
  - Designed a detailed ontology and use Neo4j to generate nodes and relationships like Paper, Author, Venue, Category, Keyword, and VenueType, and more. 
  - Current KG Size: Contains 44,159 nodes and 87,598 relationships.

- **Interactive Application**:
  - Interactive Query Interface: A Streamlit app with a chatbox that leverages OpenAI to translate user requests into Cypher queries, retrieving data directly from the KG, and provides answers.
  - Traditional Research Page: Allows users to explore the KG using standard research techniques.
 
## Ontology Overview

The KG is structured around the following main entities and relationships:
- Entities:
    - Paper (Attributes: paperID, title, DOI, yearPublication, etc.)
    - Author (Attributes: authorName, authorID, affiliation)
    - Venue (Attributes: venueName, venueID, impactFactor)
    - Keyword (Attributes: keywordName, keywordID)
    - Category (Attributes: categoryID, categoryName, description)
    - VenueType (Attributes: typeName)
- Relationships:
    - writtenBy: Connects Paper to Author
    - publishedIn: Connects Paper to Venue
    - hasKeyword: Connects Paper to Keyword
    - belongsTo: Connects Paper to Category
    - hasType: Connects Venue to VenueType
    - cites: Connects Paper to another Paper (citation relationship)
<div align="center">
<img width="381" alt="image" src="https://github.com/user-attachments/assets/1e89ee0c-7417-4053-a45f-c3cc7e376ddc">
</div>

## Try It Out
- **Live Demo**: Experience the app firsthand by accessing it [here](https://kg-research-ai-papers.streamlit.app/).
- **Demo Video**: Watch a demonstration of the app in action.


https://github.com/user-attachments/assets/db47741b-9c69-42f4-b5bf-7e986d02a556

## Repository Structure

This repository contains the following elements:

- **[1-fetch-clean-prepare-data.ipynb](https://github.com/SafaeLh/research_papers/blob/main/1-fetch-clean-prepare-data.ipynb)**: Notebook for fetching, cleaning, and preparing the data.
- **df1_2_6_full.csv**: DataFrame resulting from the first notebook.
- **[Folder 2-KG-construction](https://github.com/SafaeLh/research_papers/tree/main/2-KG-construction)**: This folder contains all files related to the construction of the Knowledge Graph (KG):
    - neo4j-KG-construction.ipynb: Notebook for constructing the KG.
    - [entity_dataframes]: All entity DataFrames used in the construction of the KG.
    - KG_ontology: File representing the ontology of the KG.

- **[Folder 3-Streamlit-code](https://github.com/SafaeLh/research_papers/tree/main/3-Streamlit-code)**: This folder contains the code for the Streamlit application:



## Getting Started
To run this project locally, follow these steps:

**Prerequisites**
- Python 3.8+
- Neo4j Desktop or Neo4j AuraDB instance
- Streamlit
- OpenAI API key for chat functionality

**Installation**
1. Clone the repository:
   
``` 
git clone https://github.com/yourusername/yourrepository.git
```

 ``` 
 cd yourrepository
```
 
2. Install the required Python packages:

``` 
pip install -r requirements.txt
```

3. Configure your OpenAI API key in the Streamlit app.

**Usage**
1. Open the Streamlit app in your browser or Run the Streamlit app:
   
``` 
streamlit run Chat.py
```

2. *Interacting with the Chatbox*: Type your query in natural language. The app will translate your query into Cypher, execute it against the KG, and display the results.
   
3. *Traditional Search Page*: Navigate through the KG using standard research methods to explore connections between papers, authors, and more.

## Future Enhancements
- Add more data sources to enrich the KG.
- Implement advanced analytics and visualization capabilities.
- Expand the ontology with new entities and relationships.

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.

## License
This project is licensed under the MIT License.














