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
    def __init__(self, embeddings, llm, session):
        self.embeddings = embeddings
        self.llm = llm
        self.session = session
        self.vector_store_service = VectorStoreService(embeddings)

    def _get_default_prompt(self):
        return """Create a LinkedIn post summarizing insights from the context.
               Keep focus on create databricks tips of implementing and best practices.
               Keep it under 300 words.
               Keep it simple for people read and direct.
               Add emojis to make it engaging.
               Do not use ** .
               Do not mention any of the sources or books.
               Do not include any links or references.
               Do not include any information from the context that is not relevant to the post."""

    async def _generate_single_post(self, vector_store, query: str) -> LinkedInPost:
        def _generate():
            qa_chain = RetrievalQA.from_chain_type(
                retriever=vector_store.as_retriever(),
                llm=self.llm,
                chain_type="stuff"
            )
            return qa_chain.invoke(query)
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, _generate)
            return LinkedInPost(content=result["result"])

    async def generate_posts(self, num_posts: int = 3, custom_prompt: str | None = None) -> List[LinkedInPost]:
        try:
            vector_store = await self.vector_store_service.update_vector_store()
            query = custom_prompt if custom_prompt else self._get_default_prompt()
            
            tasks = []
            for _ in range(num_posts):
                task = self._generate_single_post(vector_store, query)
                tasks.append(task)
            
            posts = await asyncio.gather(*tasks)
            logger.info("Successfully generated %d posts", num_posts)
            return posts
        except Exception as e:
            logger.error("Error generating posts: %s", str(e))
            raise