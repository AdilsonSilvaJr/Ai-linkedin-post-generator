import os
import asyncio
import logging
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
from langchain_chroma import Chroma
from chromadb.config import Settings
from chromadb import PersistentClient
from ..models.vector_store_models import VectorStoreStatus

from ..utils.vector_store import (
    calculate_file_hash,
    load_existing_hashes,
    save_file_hashes,
)
from ..utils.pdf_processor import load_pdf

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.source_folder = "./sources"
        self.vector_db_path = "vector_db"
        self.hash_store_path = os.path.join(self.vector_db_path, "hash_store.txt")
        self.chroma_settings = Settings(
            anonymized_telemetry=False,
            is_persistent=True,
            persist_directory=self.vector_db_path
        )
        self.chroma_client = PersistentClient(
            path=self.vector_db_path,
            settings=self.chroma_settings
        )

    async def get_status(self) -> VectorStoreStatus:
        collection = self.chroma_client.get_or_create_collection("linkedin_posts")
        existing_hashes = await load_existing_hashes(self.hash_store_path)
        return VectorStoreStatus(
            total_documents=collection.count(),
            collection_name="linkedin_posts",
            files_processed=existing_hashes
        )

    async def _check_files_changed(self) -> Dict[str, bool]:
        logger.info("Checking for file changes...")
        if not os.path.exists(self.vector_db_path):
            os.makedirs(self.vector_db_path, exist_ok=True)
            logger.info(f"Created vector_db_path: {self.vector_db_path}")
            
        existing_hashes = await load_existing_hashes(self.hash_store_path)
        files_status = {}
        
        pdf_files = [f for f in os.listdir(self.source_folder) if f.endswith('.pdf')]
        
        for file_name in pdf_files:
            file_path = os.path.join(self.source_folder, file_name)
            current_hash = await calculate_file_hash(file_path)
            
            needs_update = (file_name not in existing_hashes or 
                          existing_hashes[file_name] != current_hash)
            files_status[file_name] = {
                'needs_update': needs_update,
                'current_hash': current_hash
            }
            logger.info(f"File {file_name} needs update: {needs_update}")
            
        return files_status

    async def update_vector_store(self):
        """Update vector store asynchronously."""
        try:
            logger.info("Updating vector store...")
            files_status = await self._check_files_changed()
            files_to_update = [f for f, status in files_status.items() 
                             if status['needs_update']]
            logger.info(f"Files to update: {files_to_update}")

            def _get_or_create_collection():
                return Chroma(
                    client=self.chroma_client,
                    collection_name="linkedin_posts",
                    embedding_function=self.embeddings,
                    persist_directory=self.vector_db_path
                )

            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as pool:
                vector_store = await loop.run_in_executor(pool, _get_or_create_collection)

            updated_hashes = {}
            for file_name in files_to_update:
                file_path = os.path.join(self.source_folder, file_name)
                documents = await load_pdf(file_path)
                
                def _process_documents():
                    nonlocal vector_store
                    if vector_store is None:
                        vector_store = Chroma.from_documents(
                            documents,
                            self.embeddings,
                            collection_name="linkedin_posts",
                            client=self.chroma_client
                        )
                    else:
                        vector_store.add_documents(documents)
                    return vector_store

                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as pool:
                    vector_store = await loop.run_in_executor(pool, _process_documents)
                
                updated_hashes[file_name] = files_status[file_name]['current_hash']

            if updated_hashes:
                existing_hashes = await load_existing_hashes(self.hash_store_path)
                existing_hashes.update(updated_hashes)
                await save_file_hashes(existing_hashes, self.hash_store_path)

            return vector_store or Chroma(
                client=self.chroma_client,
                collection_name="linkedin_posts",
                embedding_function=self.embeddings,
                persist_directory=self.vector_db_path
            )

        except Exception as e:
            logger.error(f"Error updating vector store: {str(e)}")
            raise