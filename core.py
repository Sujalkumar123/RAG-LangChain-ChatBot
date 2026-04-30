import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_classic import hub
from langchain_classic.callbacks.base import BaseCallbackHandler
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.history_aware_retriever import (
    create_history_aware_retriever,
)
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_google_genai import ChatGoogleGenerativeAI

from ingestion import vectorstore
from logger import *


# Custom handler: prints tokens live
class PrintTokenHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)


def run_llm_from_docs(query: str, chat_history: List[Dict[str, Any]] = []):

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)

    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 15, "score_threshold": 0.75},
    )
    history_aware_retriever = create_history_aware_retriever(
        llm=llm,
        retriever=retriever,
        prompt=rephrase_prompt,
    )
    retrieval_chain = create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=combine_docs_chain,
    )

    result = retrieval_chain.invoke(
        input={"input": query, "chat_history": chat_history}
    )
    return result


# def run_general_llm(query: str, chat_history: List[Dict[str, Any]] = []):
#     # Prepare messages for the model: system + history + new query
#     messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
#     messages.extend(chat_history)
#     messages.append({"role": "user", "content": query})
#     result = llm.invoke(messages)
#     return result


def run_general_llm(query: str, chat_history: List[tuple] = []):
    # Prepare messages for the model: system + history + new query
    messages = [("system", "You are a helpful AI assistant")]
    messages.extend(chat_history)
    messages.append(("user", query))
    result = llm.invoke(messages)
    return result


# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful AI assistant."),
#         MessagesPlaceholder("chat_history"),
#         ("user", "{query}"),
#     ]
# )

# def run_general_llm(query: str, chat_history: List[Dict[str, Any]] = []):
#     # Format the prompt with query + history
#     formatted_prompt = prompt.format_prompt(query=query, chat_history=chat_history)
#     # Call the model
#     result = llm.invoke(formatted_prompt.to_messages())
#     return result
# site:reddit.com "ai" "is there any tool"

# if __name__ == "__main__":
#     from pprint import pprint

#     # set a breakpoint on the next line
#     # run_llm_from_docs("What are ai agents?")
#     run_general_llm("WHat is dragonball")
#     run_general_llm1("what is demon slayer infinity castle")
