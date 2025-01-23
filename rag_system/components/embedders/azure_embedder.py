#this file embeds data and uploads data to the vector database

from .embedder_base import EmbedderBase
from rag_system.services.azure_openai import AzureOpenAIClient
from rag_system.core.data_chunk import DataChunk
from typing import List
from rag_system.services.azure_ai_search import AzureAISearch

class AzureEmbedder(EmbedderBase):
    def __init__(self, index_name = "dama_index"):
        #embed parameters
        self.embed_client = AzureOpenAIClient()
        # search (vector db) parameters
        self.index_name = index_name 
        self.search_client = AzureAISearch()

    def embed(self, text) -> List[float]: 
        '''
        Embeds the text using the Azure OpenAI service
        '''
        return self.embed_client.generate_embeddings(text)
    
    def embed_and_load(self, data: List[DataChunk]) -> None:
        '''
        Embeds and uploads the embedded item to the index
        '''
        try:
            # Call the create_index function from Azure search service 
            self.search_client.create_index(self.index_name, inspections = True)

            contents = [d.content for d in data]        
            content_embeddings = [self.embed(content) for content in contents]

            all_data_chunk = [item.to_dictionary() for item in data]
            
            for i, item in enumerate(all_data_chunk): 
                item["content_embedding"] = content_embeddings[i]
            self.search_client.upload_embeddings(self.index_name, all_data_chunk)
            print("Successfully loaded the embedded data to the index")
        except Exception as e:
            print( f"An error occurred: {str(e)}")
        