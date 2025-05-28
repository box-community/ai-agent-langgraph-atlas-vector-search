import os
from dotenv import load_dotenv
from langchain.agents import tool
from langchain_mongodb import (
    MongoDBAtlasVectorSearch,
)

from langchain_mongodb.retrievers.full_text_search import (
    MongoDBAtlasFullTextSearchRetriever,
)
from langchain_openai import OpenAIEmbeddings

from langchain_mongodb.index import create_fulltext_search_index
from pymongo import MongoClient

load_dotenv()
DEMO_FOLDER_PARENT_ID = "0"  # Root folder ID for Box
SAMPLE_DATA_LOCAL_PATH = "sample_data/Q4 Tech earnings-Demo"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")


# Define a vector search tool
@tool
def vector_search(user_query: str) -> str:
    """
    Retrieve information using vector search to answer a user query.
    """
    # Instantiate the vector store
    vector_store = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=MONGODB_URI,
        namespace="langchain_db.earnings_reports",
        embedding=OpenAIEmbeddings(),
        index_name="vector_index",  # Name of the vector index
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},  # Retrieve top 5 most similar documents
    )

    results = retriever.invoke(user_query)

    # Concatenate the results into a string
    context = "\n\n".join(
        [f"{doc.metadata['title']}: {doc.page_content}" for doc in results]
    )
    return context


# Define a full-text search tool
@tool
def full_text_search(user_query: str) -> dict:
    """
    Retrieve movie plot content based on the provided title.
    """
    client = MongoClient(MONGODB_URI)
    collection = client["langchain_db"]["earnings_reports"]

    # Initialize the retriever
    retriever = MongoDBAtlasFullTextSearchRetriever(
        collection=collection,  # MongoDB Collection in Atlas
        search_field="text",  # Name of the field to search
        search_index_name="search_index",  # Name of the search index
        top_k=1,  # Number of top results to return
    )
    results = retriever.invoke(user_query)

    for doc in results:
        if doc:
            del doc.metadata["embedding"]
            doc.metadata["page_content"] = doc.page_content
            return doc.metadata
        else:
            return "Document not found"


def main() -> None:
    # Test the tool
    print("\nTesting vector search tool...")
    print("--" * 40)
    test_results = vector_search.invoke(
        "What are the challenges facing tech companies in 2026?"
    )
    print(test_results)
    print("--" * 40)

    # Test the tool
    print("\n\nTesting full search tool...")
    print("--" * 40)
    result = full_text_search.invoke("largest driver of expense growth")
    print(result)


if __name__ == "__main__":
    main()
