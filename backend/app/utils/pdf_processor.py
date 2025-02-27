import os
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

async def load_pdf(file_path: str):
    """Load a single PDF file asynchronously."""
    logger.info(f"Loading PDF file: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents from PDF file: {file_path}")
    return documents

async def split_documents(documents, chunk_size=500, chunk_overlap=100):
    """Split documents asynchronously."""
    def _split():
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter.split_documents(documents)
    
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, _split)