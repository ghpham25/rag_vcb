import os 
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters
)
from azure.search.documents import SearchClient
import json
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.models import VectorizedQuery, VectorizableTextQuery
from azure.search.documents import SearchItemPaged
from rag_system.services.azure_openai import AzureOpenAIClient

load_dotenv(override=True)
class AzureAISearch(): 
    def __init__(self):
        self.search_service_endpoint = os.getenv("SEARCH_ENDPOINT")
        self.search_service_key = os.getenv("SEARCH_KEY")
        self.azure_openai_client = AzureOpenAIClient()
        self.azure_openai_embedding_dimensions = self.azure_openai_client.get_parameters()["azure_openai_embedding_dimensions"]

    def create_index_client(self): 
        return SearchIndexClient(endpoint=self.search_service_endpoint, credential=AzureKeyCredential( self.search_service_key))

    def create_search_client(self, index_name): 
        return SearchClient(endpoint=self.search_service_endpoint, index_name=index_name, credential=AzureKeyCredential(self.search_service_key))

    def create_index(self, index_name, inspections = False): 

        index_client = self.create_index_client()
            # Step 1: Try to get the existing index
        try:
            existing_index = index_client.get_index(index_name)
            print(f"Index '{index_name}' exists. Cancelling the action.")
            return 

        except ResourceNotFoundError:
            # If the index does not exist, this will be caught and we proceed without deletion
            print(f"Index '{index_name}' does not exist. Proceeding to create a new one.")

        fields = [
        SimpleField(name=os.getenv("CHUNK_ID"), type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
        SearchableField(name=os.getenv("CONTENT"), type=SearchFieldDataType.String),
        SearchableField(name=os.getenv("SOURCE"), type=SearchFieldDataType.String,
                        filterable=True),
        SimpleField(name=os.getenv("OFFSET"), type=SearchFieldDataType.Int32),
        SimpleField(name=os.getenv("PAGE_NUMBER"), type=SearchFieldDataType.Int32,
                    filterable=True),
        SearchField(name=os.getenv("EMBEDDING"), type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=self.azure_openai_embedding_dimensions, vector_search_profile_name="myHnswProfile"),
    ]
        
        # Configure the vector search configuration

        openai_client_params = self.azure_openai_client.get_parameters()

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="myHnsw"
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="myHnsw",
                    vectorizer_name="myVectorizer"
                )
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    vectorizer_name="myVectorizer",
                    parameters=AzureOpenAIVectorizerParameters(
                        resource_url=openai_client_params["azure_openai_endpoint"],
                        deployment_name=openai_client_params["azure_openai_embedding_model"],
                        model_name=openai_client_params["azure_openai_embedding_model"],
                        api_key=openai_client_params["azure_openai_key"]
                    )
                )
            ]
        )

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )

        # Create the semantic settings with the configuration
        semantic_search = SemanticSearch(configurations=[semantic_config])

        # Create the search index with the semantic settings
        index = SearchIndex(name=index_name, fields=fields,
                            vector_search=vector_search, semantic_search=semantic_search)
        result = index_client.create_or_update_index(index)
        print(f'{result.name} created')


        if inspections:
            for field in index_client.get_index(index_name).fields:
                print(f"Name: {field.name}")
                print(f"Type: {field.type}")
                print(f"Searchable: {field.searchable}")
                print(f"Filterable: {field.filterable}")
                print(f"Sortable: {field.sortable}")
                print(f"Facetable: {field.facetable}")
                print(f"Key: {field.key}")
                print("-" * 40)

    def upload_embeddings(self, index_name, data): 
        search_client = self.create_search_client(index_name)
        search_client.upload_documents(documents=data)
        
    def semantic_search(self, index_name, question): 
        vector_query = VectorizableTextQuery(text=question, 
                                            k_nearest_neighbors=os.getenv("K_NEAREST_NEIGHBORS"), 
                                            fields = os.getenv("SEARCH_FIELDS"), 
                                            )
        
        search_client = self.create_search_client(index_name)
        results = search_client.search(search_text = question, 
                                       vector_queries=[vector_query], 
                                       select= os.getenv("SELECT_FIELDS"), 
                                       top = os.getenv("TOP_RESULTS")
                                       )
        readable_results = [result for result in results]
        return readable_results 