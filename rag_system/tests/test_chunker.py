# Description: This file contains the test cases for the loader module.
from rag_system.components.chunkers.fixed_size_chunker import FixedSizePDFChunker

def test_chunker():
    chunker = FixedSizePDFChunker()
    print("Test chunker passed")
if __name__ == "__main__":
    # url = "/Users/giangpham/Desktop/VCB/test/data/small.pdf"
    test_chunker()