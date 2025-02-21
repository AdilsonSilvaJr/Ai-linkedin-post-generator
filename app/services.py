import os
import asyncio
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from chromadb.config import Settings
from chromadb import PersistentClient  # Add this import

from .models import LinkedInPost
from .vector_store import (
    calculate_file_hash,
    load_existing_hashes,
    save_file_hashes,
)
from .pdf_processor import load_pdf

# Configure logging - Move this to the very top after imports
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class PostGeneratorService:
    def __init__(self, embeddings, llm, session):
        self.embeddings = embeddings
        self.llm = llm
        self.session = session
        self.source_folder = "./sources"
        self.vector_db_path = "vector_db"
        self.hash_store_path = os.path.join(self.vector_db_path, "hash_store.txt")
        self.chroma_settings = Settings(
            anonymized_telemetry=False,
            is_persistent=True,
            persist_directory=self.vector_db_path
        )
        # Initialize ChromaDB client
        self.chroma_client = PersistentClient(
            path=self.vector_db_path,
            settings=self.chroma_settings
        )

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

    async def _update_vector_store(self):
        """Update vector store asynchronously."""
        try:
            logger.info("Updating vector store...")
            files_status = await self._check_files_changed()
            files_to_update = [f for f, status in files_status.items() 
                             if status['needs_update']]
            logger.info(f"Files to update: {files_to_update}")

            # Initialize or load the collection
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

            # Load and process only the files that need updating
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
                
                # Update hash for processed file
                updated_hashes[file_name] = files_status[file_name]['current_hash']

            # Save updated hashes if any files were processed
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

    async def _generate_single_post(self, vector_store, query: str) -> LinkedInPost:
        """Generate a single post asynchronously."""
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
        """Generate multiple posts concurrently."""
        try:
            vector_store = await self._update_vector_store()
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
