# Description: This file contains the test cases for the loader module.
from rag_system.components.loaders.azure_pdf_loader import AzurePDFLoader

def test_loader(url):
    loader = AzurePDFLoader()
    data_chunks = loader.load(url)
    assert len(data_chunks) > 0
    for chunk in data_chunks: 
        print(chunk)

if __name__ == "__main__":
    url = "/Users/giangpham/Desktop/VCB/test/data/small.pdf"
    test_loader(url)