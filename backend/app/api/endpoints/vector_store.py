import os
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ...dependencies import get_embeddings
from ...services.vector_store_service import VectorStoreService

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/update")
async def update_vector_store(
    embeddings=Depends(get_embeddings),
    files: List[UploadFile] = File(...)
):
    try:
        # Ensure the directory exists
        os.makedirs('./sources', exist_ok=True)

        # Save uploaded files to the directory
        for file in files:
            file_path = os.path.join('./sources', file.filename)
            with open(file_path, 'wb') as f:
                f.write(await file.read())

        # Update the vector store
        service = VectorStoreService(embeddings)
        await service.update_vector_store('./sources')

        return {"message": "Vector store updated successfully"}
    except Exception as e:
        logger.error(f"Error updating vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))