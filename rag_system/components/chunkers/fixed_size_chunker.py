#This file chunks a page data into smaller sections 

from typing import List
from rag_system.components.chunkers.chunker_base import ChunkerBase
from rag_system.core.data_chunk import DataChunk
import re

class FixedSizePDFChunker(ChunkerBase):
    def __init__(self, chunk_size = 1000, section_overlap = 100, sentence_search_limit = 100):
        self.chunk_size = chunk_size
        self.section_overlap = section_overlap
        self.sentence_search_limit = sentence_search_limit
    
    def chunk_helper(self, data: List[DataChunk]):
        SENTENCE_ENDINGS = [".", "!", "?"]
        WORDS_BREAKS = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]

        def find_page( offset):
            l = len(data)
            for i in range(l - 1):
                if offset >= data[i].offset and offset < data[i + 1].offset:
                    return i
            return l - 1

        all_text = "".join(d.content for d in data)
        length = len(all_text)

        start = 0
        end = length

        while start + self.section_overlap < length: 
                    last_word = -1
        end = start + self.chunk_size

        if end > length:
            end = length
        else:
            # Try to find the end of the sentence
            while end < length and (end - start - self.chunk_size) < self.sentence_search_limit and all_text[end] not in SENTENCE_ENDINGS:
                if all_text[end] in WORDS_BREAKS:
                    last_word = end
                end += 1
            if end < length and all_text[end] not in SENTENCE_ENDINGS and last_word > 0:
                end = last_word # Fall back to at least keeping a whole word
        if end < length:
            end += 1

        # Try to find the start of the sentence or at least a whole word boundary
        last_word = -1
        while start > 0 and start > end - self.chunk_size - 2 * self.sentence_search_limit and all_text[start] not in SENTENCE_ENDINGS:
            if all_text[start] in WORDS_BREAKS:
                last_word = start
            start -= 1
        if all_text[start] not in SENTENCE_ENDINGS and last_word > 0:
            start = last_word
        if start > 0:
            start += 1
        
        section_text = all_text[start:end]
        yield (section_text, find_page(start), start)

        last_table_start = section_text.rfind("<table")
        if (last_table_start > 2 * self.sentence_search_limit and last_table_start > section_text.rfind("</table")):
            # If the section ends with an unclosed table, we need to start the next section with the table.
            # If table starts inside SENTENCE_SEARCH_LIMIT, we ignore it, as that will cause an infinite loop for tables longer than MAX_SECTION_LENGTH
            # If last table starts inside SECTION_OVERLAP, keep overlapping
            start = min(end - self.section_overlap, start + last_table_start)
        else:
            start = end - self.section_overlap
        
        if start + self.section_overlap < end:
            yield (all_text[start:end], find_page(start), start)
    
    def chunk(self, data: List[DataChunk]) -> List[DataChunk]:
        source_url = data[0].source
        chunked_data = []

        for i, (section_text, page_num, offset) in self.chunk_helper(data):
            chunk_id = re.sub("[^0-9a-zA-Z_-]","_",f"{source_url}-{i}")
            chunked_data.append(DataChunk(content = section_text, 
                                          source = source_url, 
                                          offset = offset, 
                                          page_number = page_num, 
                                          chunk_id = chunk_id))
        return chunked_data