import os
from typing import List
from dotenv import load_dotenv
from langchain_box.document_loaders import BoxLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb.index import create_fulltext_search_index
from pymongo import MongoClient
from box_sdk_gen import (
    BoxCCGAuth,
    CCGConfig,
    BoxClient,
    FileTokenStorage,
    BoxAPIError,
)
from box_sdk_gen import (
    CreateFolderParent,
    UploadFileAttributes,
    UploadFileAttributesParentField,
)

load_dotenv()
DEMO_FOLDER_PARENT_ID = "0"  # Root folder ID for Box
SAMPLE_DATA_LOCAL_PATH = "sample_data/Q4 Tech earnings-Demo"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")


def get_box_client() -> BoxClient:
    """
    Initialize and return a Box client using the Box CCG Auth.
    """
    client_id = os.getenv("BOX_CLIENT_ID")
    client_secret = os.getenv("BOX_CLIENT_SECRET")
    user_id = os.getenv("BOX_SUBJECT_ID")

    # Create a BoxCCGConfig instance
    box_config = CCGConfig(
        client_id=client_id,
        client_secret=client_secret,
        user_id=user_id,
        token_storage=FileTokenStorage(".ccg.db"),
    )
    # Create a BoxCCGAuth instance
    box_auth = BoxCCGAuth(box_config)
    # Create a BoxClient instance
    return BoxClient(box_auth)


def upload_sample_data(
    box_client: BoxClient,
    parent_folder_id: str = DEMO_FOLDER_PARENT_ID,
    local_folder_path: str = SAMPLE_DATA_LOCAL_PATH,
) -> str:
    try:
        box_folder = box_client.folders.create_folder(
            name=os.path.basename(local_folder_path),
            parent=CreateFolderParent(id=parent_folder_id),
        )
    except BoxAPIError as e:
        if e.response_info.body["status"] == 409:
            # Folder already exists, get its ID
            box_folder = box_client.folders.get_folder_by_id(
                e.response_info.body["context_info"]["conflicts"][0]["id"]
            )

    print(f"Created folder: {box_folder.name} ({box_folder.id})")

    # Upload files to the new folder
    local_folder_path = os.path.abspath(local_folder_path)
    for root, _, files in os.walk(local_folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            parent = UploadFileAttributesParentField(id=box_folder.id, type="folder")
            file_attributes = UploadFileAttributes(
                name=file_name,
                parent=parent,
            )
            with open(file_path, "rb") as file_stream:
                try:
                    box_file = box_client.uploads.upload_file(
                        attributes=file_attributes, file=file_stream
                    ).entries[0]
                    print(f"Uploaded file: {box_file.name} ({box_file.id})")
                except BoxAPIError as e:
                    if e.response_info.body["status"] == 409:
                        print(
                            f"File already exists: {file_name} ({e.response_info.context_info['conflicts']['id']})"
                        )

    return box_folder.id


def load_documents_from_box(
    box_client: BoxClient,
    box_folder_id: str,
) -> List[Document]:
    auth_token = box_client.auth.retrieve_token().access_token
    loader = BoxLoader(
        box_developer_token=auth_token,
        box_folder_id=box_folder_id,  # type: ignore
    )
    data = loader.load()

    # Split PDF into documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    return text_splitter.split_documents(data)


def create_vector_index(docs: List[Document]) -> None:
    # drop collection if it exists
    client = MongoClient(MONGODB_URI)
    db = client["langchain_db"]
    if "earnings_reports" in db.list_collection_names():
        db["earnings_reports"].drop()

    # Initialize the MongoDB Atlas vector search index
    embedding_model = OpenAIEmbeddings()
    # Instantiate vector store
    vector_store = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=MONGODB_URI,
        namespace="langchain_db.earnings_reports",
        embedding=embedding_model,
        index_name="vector_index",
    )

    # Add data to the vector store
    vector_store.add_documents(docs)

    # Use helper method to create the vector search index
    vector_store.create_vector_search_index(dimensions=1536)


def create_search_index() -> None:
    # Connect to your cluster
    client = MongoClient(MONGODB_URI)
    # Use helper method to create the search index
    create_fulltext_search_index(
        collection=client["langchain_db"]["earnings_reports"],
        field="text",
        index_name="search_index",
    )


def main() -> None:
    # Test box connection
    try:
        box_client = get_box_client()
        user_info = box_client.users.get_user_me()
        print(f"Connected to Box as user: {user_info.name} (ID: {user_info.id})")
    except BoxAPIError as e:
        print(f"Failed to connect to Box: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Upload sample data
    try:
        folder_id = upload_sample_data(box_client)
        print(f"Sample data uploaded to folder ID: {folder_id}")
    except BoxAPIError as e:
        print(f"Failed to upload sample data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during upload: {e}")

    docs = load_documents_from_box(box_client, folder_id)

    # Create vector index
    try:
        create_vector_index(docs)
        print("Vector index created successfully.")
    except Exception as e:
        print(f"Failed to create vector store: {e}")

    # Create search index
    try:
        create_search_index()
        print("Search index created successfully.")
    except Exception as e:
        print(f"Failed to create search index: {e}")


if __name__ == "__main__":
    main()
