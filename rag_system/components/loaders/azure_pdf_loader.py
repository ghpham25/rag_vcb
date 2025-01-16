from typing import List
from rag_system.core.data_chunk import DataChunk
from .loader_base import DataLoaderBase
from rag_system.services.azure_document_intelligence import AzureDocumentIntelligenceClient

class AzurePDFLoader(DataLoaderBase): 
    def __init__(self): 
        self.pdf_loader_client = AzureDocumentIntelligenceClient()
        
    def load(self, pdf_url) -> List[DataChunk]:
        '''
        Load the pdf_url to a list of DataChunks, sectioning by page number.
        '''
        page_map = self.pdf_loader_client.get_page_map(pdf_url)
        data_chunks = []
        for page_num, offset, page_text in page_map: 
            data_chunks.append(DataChunk(source=pdf_url, content = page_text, offset=offset, page_number = page_num))
        return data_chunks
    