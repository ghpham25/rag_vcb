import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import json

load_dotenv(override = True)
class AzureOpenAIClient:
    def __init__(self):
        self.subscription_key = os.getenv('AZURE_OPENAI_SUBSCRIPTION_KEY')
        self.azure_openai_endpoint = os.environ["OPENAI_ENDPOINT"]
        self.azure_openai_key = os.getenv("OPENAI_KEY", "") if len(os.getenv("OPENAI_KEY", "")) > 0 else None
        self.azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        self.azure_openai_embedding_dimensions = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", 1024))
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        self.openai_credential = DefaultAzureCredential()
        self.client = self.get_client()

    def get_client(self): 
        return AzureOpenAI(
            api_key = self.azure_openai_key,  
            api_version = "2024-06-01",
            azure_endpoint = self.azure_openai_endpoint
            )
    
    def generate_embeddings(self, text):
        return self.client.embeddings.create(input = text, model = self.azure_openai_embedding_deployment, dimensions = self.azure_openai_embedding_dimensions).data[0].embedding 
        
    def get_parameters(self): 
        return {
            "azure_openai_key": self.azure_openai_key,
            "azure_openai_endpoint": self.azure_openai_endpoint,
            "azure_openai_embedding_model": self.azure_openai_embedding_deployment,
            "azure_openai_embedding_dimensions": self.azure_openai_embedding_dimensions,
            "azure_openai_api_version": self.azure_openai_api_version
        }
    