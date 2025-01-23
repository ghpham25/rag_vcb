# Description: This file contains the test cases for the loader module.
from rag_system.components.loaders.azure_pdf_loader import AzurePDFLoader
from rag_system.components.chunkers.fixed_size_chunker import FixedSizePDFChunker
from rag_system.components.embedders.azure_embedder import AzureEmbedder

def test_loader(url):
    '''
    loading document to the index/ vector database
    '''
    loader = AzurePDFLoader()
    data_chunks_by_page = loader.load(url)
    assert len(data_chunks_by_page) > 0    
    chunker = FixedSizePDFChunker()
    chunked_data = chunker.chunk(data_chunks_by_page)
    azure_embedder = AzureEmbedder()
    azure_embedder.embed_and_load(chunked_data)

if __name__ == "__main__":
    url = "/Users/giangpham/Desktop/VCB/test/data/small.pdf"
    test_loader(url)