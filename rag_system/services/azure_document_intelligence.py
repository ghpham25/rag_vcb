from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import sys 
import os 
import html
import re
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from rag_system.utils.general_pdf_utils import table_to_html

class AzureDocumentIntelligenceClient: 
    def __init__(self):
        self.form_recognizer_key = os.getenv("FORM_RECOGNIZER_SUBSCRIPTION_KEY")
        self.form_recognizer_enpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
        self.client = DocumentAnalysisClient(self.form_recognizer_enpoint, AzureKeyCredential(self.form_recognizer_key))
    
    def get_page_map(self, document_url: str) -> list: 
        """
        Generate a mapping of pages to text content, including tables in HTML format.
        Uses Azure Form Recognizer but relies on general utilities like `table_to_html`.

        Args:
            document_url (str): Path to the PDF document.

        Returns:
            list: A list of tuples containing page number, offset, and page text with tables.
        """

        page_map = []
        offset = 0
        form_recognizer_client = self.client
        with open(document_url, "rb") as f:
            poller = form_recognizer_client.begin_analyze_document("prebuilt-layout", f)
        document_results = poller.result()
        for page_num, page in enumerate(document_results.pages):
            tables_on_page = [table for table in document_results.tables if table.bounding_regions[0].page_number == page_num + 1]
            # mark all positions of the table spans in the page
            page_offset = page.spans[0].offset
            page_length = page.spans[0].length
            table_chars = [-1]*page_length
            for table_id, table in enumerate(tables_on_page):
                for span in table.spans:
                    # replace all table spans with "table_id" in table_chars array
                    for i in range(span.length):
                        idx = span.offset - page_offset + i
                        if idx >=0 and idx < page_length:
                            table_chars[idx] = table_id

            # build page text by replacing charcters in table spans with table html
            page_text = ""
            added_tables = set()
            for idx, table_id in enumerate(table_chars):
                if table_id == -1:
                    page_text += document_results.content[page_offset + idx]
                elif not table_id in added_tables:
                    page_text += table_to_html(tables_on_page[table_id])
                    added_tables.add(table_id)

            page_text += " "
            page_map.append((page_num, offset, page_text))
            offset += len(page_text)
        return page_map      

    




            




    
 


    