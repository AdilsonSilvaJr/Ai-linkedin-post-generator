import os
import logging
from typing import List
import asyncio
from langchain_chroma import Chroma
from chromadb.config import Settings
from chromadb import PersistentClient
from ..utils.vector_store import (
    calculate_file_hash,
    load_existing_hashes,
    save_file_hashes,
)
from ..utils.pdf_processor import load_pdf

logger = logging.getLogger(__name__)

class VectorStoreService:
    _instance = None

    def __new__(cls, embeddings):
        if cls._instance is None:
            cls._instance = super(VectorStoreService, cls).__new__(cls)
            cls._instance._initialize(embeddings)
        return cls._instance

    def _initialize(self, embeddings):
        self.embeddings = embeddings
        self.vector_db_path = "vector_db"
        self.collection_name = "linkedin_posts"
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            persist_directory=self.vector_db_path,
            embedding_function=self.embeddings,
        )

    async def update_vector_store(self, source_dir: str):
        hash_file_path = os.path.join(self.vector_db_path, "hashes.txt")
        
        # Check if these functions are actually async
        existing_hashes = await load_existing_hashes(hash_file_path) if asyncio.iscoroutinefunction(load_existing_hashes) else load_existing_hashes(hash_file_path)

        # Process each file in the source directory
        for file_name in os.listdir(source_dir):
            file_path = os.path.join(source_dir, file_name)
            
            # Check if this function is actually async
            file_hash = await calculate_file_hash(file_path) if asyncio.iscoroutinefunction(calculate_file_hash) else calculate_file_hash(file_path)

            # Check if the file has already been processed
            if file_hash in existing_hashes:
                logger.info(f"File {file_name} already processed.")
                continue

            # Check if this function is actually async
            documents = await load_pdf(file_path) if asyncio.iscoroutinefunction(load_pdf) else load_pdf(file_path)
            
            # This is definitely not async in LangChain
            self.vector_store.add_documents(documents)

            # Save the new hash
            existing_hashes[file_hash] = file_name

        # Check if this function is actually async
        if asyncio.iscoroutinefunction(save_file_hashes):
            await save_file_hashes(existing_hashes, hash_file_path)
        else:
            save_file_hashes(existing_hashes, hash_file_path)