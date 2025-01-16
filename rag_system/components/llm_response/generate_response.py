from azure_search import AzureSearch
from rag_system.services.azure_openai import AzureOpenAIClient
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class LLMResponseGenerator: 
    def __init__(self):
        self.searcher = AzureSearch()
        self.llm_client = AzureOpenAIClient().get_client()
        self.chat_completion_model = os.getenv("OPENAI_CHAT_COMPLETION_MODEL_NAME")

    def generate_response(self, user_query):
        chat_history = []

        while True:
            search_results = self.searcher.search(user_query)
            data_source = [doc["sourcefile"] + ", page " + str(doc["page"]) + ": " + doc["content"].replace("\n", "").replace("\r", "") for doc in search_results]
            content = "\n".join(data_source)

            messages = [
                {"role": "system", "content": "You are an AI assistant trained to answer queries based on the following information: " + content + " Provide sourcefile and the page number you used to answer the question."}
            ] + chat_history + [{"role": "user", "content": user_query}]

            response = self.llm_client.chat.completions.create(
                model=self.chat_completion_model,
                messages=messages
            )

            answer = response.choices[0].message.content
            print(answer)

            chat_history.append({"role": "user", "content": user_query})
            chat_history.append({"role": "assistant", "content": answer})

            user_query = input("You: ")
            if user_query.lower() == "exit":
                break
