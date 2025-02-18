from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_openai import OpenAI
# from langchain_ollama import OllamaLLM
from langchain_google_genai import ChatGoogleGenerativeAI
import aiohttp
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

@lru_cache()
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@lru_cache()
def get_llm(model_name="gemini-2.0-flash-exp"):
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7
    )

# Old OpenAI implementation
# @lru_cache()
# def get_llm(model_name="gpt-4o-mini"):
#     return OpenAI(
#         api_key=os.getenv("OPENAI_API_KEY"),
#         model_name=model_name,
#         temperature=0.7
#     )

# Old Ollama implementation
# @lru_cache()
# def get_llm(model_name="qwen2.5-coder:3b"):
#     return OllamaLLM(
#         model=model_name, 
#         base_url="http://localhost:33821")

async def get_async_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    async with aiohttp.ClientSession() as session:
        yield session
