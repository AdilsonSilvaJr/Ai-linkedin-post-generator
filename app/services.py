import os
import asyncio
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS

from .models import LinkedInPost
from .vector_store import (
    calculate_file_hash,
    load_existing_hashes,
    save_file_hashes,
)
from .pdf_processor import load_pdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostGeneratorService:
    def __init__(self, embeddings, llm, session):
        self.embeddings = embeddings
        self.llm = llm
        self.session = session
        self.source_folder = "./sources"
        self.vector_db_path = "vector_db"
        self.hash_store_path = os.path.join(self.vector_db_path, "hash_store.txt")
        
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
        """
        Check which files have changed or are new.
        Returns a dictionary of {filename: needs_update}.
        """
        if not os.path.exists(self.vector_db_path):
            os.makedirs(self.vector_db_path, exist_ok=True)
            
        existing_hashes = await load_existing_hashes(self.hash_store_path)
        files_status = {}
        
        pdf_files = [f for f in os.listdir(self.source_folder) if f.endswith('.pdf')]
        
        # Check all current files
        for file_name in pdf_files:
            file_path = os.path.join(self.source_folder, file_name)
            current_hash = await calculate_file_hash(file_path)
            
            # File needs update if it's new or hash has changed
            needs_update = (file_name not in existing_hashes or 
                          existing_hashes[file_name] != current_hash)
            files_status[file_name] = {
                'needs_update': needs_update,
                'current_hash': current_hash
            }
            
        return files_status

    async def _update_vector_store(self):
        """Update vector store asynchronously."""
        try:
            # Check which files need to be updated
            files_status = await self._check_files_changed()
            files_to_update = [f for f, status in files_status.items() 
                             if status['needs_update']]
            
            # If no files need updating and vector store exists, just load it
            if not files_to_update and os.path.exists(os.path.join(self.vector_db_path, "index.faiss")):
                def _load_existing_store():
                    return FAISS.load_local(
                        self.vector_db_path,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as pool:
                    return await loop.run_in_executor(pool, _load_existing_store)

            # Load existing vector store if it exists
            vector_store = None
            if os.path.exists(os.path.join(self.vector_db_path, "index.faiss")):
                def _load_vector_store():
                    return FAISS.load_local(
                        self.vector_db_path,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as pool:
                    vector_store = await loop.run_in_executor(pool, _load_vector_store)

            # Load and process only the files that need updating
            updated_hashes = {}
            for file_name in files_to_update:
                file_path = os.path.join(self.source_folder, file_name)
                documents = await load_pdf(file_path)
                
                def _process_documents():
                    nonlocal vector_store
                    if vector_store is None:
                        vector_store = FAISS.from_documents(documents, self.embeddings)
                    else:
                        vector_store.add_documents(documents)
                    vector_store.save_local(self.vector_db_path)
                    return vector_store

                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as pool:
                    vector_store = await loop.run_in_executor(pool, _process_documents)
                
                # Update hash for processed file
                updated_hashes[file_name] = files_status[file_name]['current_hash']

            # Save updated hashes if any files were processed
            if updated_hashes:
                # Load existing hashes to preserve hashes of unchanged files
                existing_hashes = await load_existing_hashes(self.hash_store_path)
                # Update with new hashes
                existing_hashes.update(updated_hashes)
                # Save all hashes
                await save_file_hashes(existing_hashes, self.hash_store_path)

            # Ensure the vector store is saved properly
            if vector_store:
                vector_store.save_local(self.vector_db_path)
                logger.info(f"Vector store saved at {self.vector_db_path}")

            # Verify that the vector store file exists
            if not os.path.exists(os.path.join(self.vector_db_path, "index.faiss")):
                logger.info("Vector store file not found, creating a new one.")
                # Create a new vector store from the documents if the file does not exist
                all_documents = []
                for file_name in os.listdir(self.source_folder):
                    if file_name.endswith('.pdf'):
                        file_path = os.path.join(self.source_folder, file_name)
                        documents = await load_pdf(file_path)
                        all_documents.extend(documents)
                vector_store = FAISS.from_documents(all_documents, self.embeddings)
                vector_store.save_local(self.vector_db_path)
                logger.info(f"New vector store created and saved at {self.vector_db_path}")

            # Return the vector store
            return vector_store or FAISS.load_local(
                self.vector_db_path,
                self.embeddings,
                allow_dangerous_deserialization=True
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
        vector_store = await self._update_vector_store()
        query = custom_prompt if custom_prompt else self._get_default_prompt()
        
        tasks = []
        for _ in range(num_posts):
            task = self._generate_single_post(vector_store, query)
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
