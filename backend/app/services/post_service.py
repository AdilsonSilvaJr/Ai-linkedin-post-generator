import os
import asyncio
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from chromadb.config import Settings
from chromadb import PersistentClient

from ..models.post_models import LinkedInPost
from ..utils.vector_store import (
    calculate_file_hash,
    load_existing_hashes,
    save_file_hashes,
)
from ..utils.pdf_processor import load_pdf
from ..services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)

class PostGeneratorService:
    _instance = None

    def __new__(cls, embeddings, llm, session):
        if cls._instance is None:
            cls._instance = super(PostGeneratorService, cls).__new__(cls)
            cls._instance._initialize(embeddings, llm, session)
        return cls._instance

    def _initialize(self, embeddings, llm, session):
        self.embeddings = embeddings
        self.llm = llm
        self.session = session
        self.vector_db_path = "vector_db"
        self.collection_name = "linkedin_posts"
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            persist_directory=self.vector_db_path,
            embedding_function=self.embeddings,
        )

    def _get_default_prompt(self):
        return "Generate a LinkedIn post based on the provided content."

    async def _generate_single_post(self, vector_store, query: str) -> LinkedInPost:
        retriever = vector_store.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
        )
        result = qa_chain.invoke({"query": query})
        
        # It typically returns a dict with a key like 'result' or 'answer'
        if isinstance(result, dict):
            # Extract the content from the result dict
            # The exact key depends on your RetrievalQA setup
            content = result.get("result") or result.get("answer") or result.get("output") or str(result)
        else:
            content = str(result)
            
        return LinkedInPost(content=content)

    async def generate_posts(self, num_posts: int, custom_prompt: str | None) -> List[LinkedInPost]:
        prompt = custom_prompt if custom_prompt else self._get_default_prompt()
        posts = []
        for _ in range(num_posts):
            post = await self._generate_single_post(self.vector_store, prompt)
            posts.append(post)
        return posts