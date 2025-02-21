import logging
from fastapi import APIRouter, Depends, HTTPException
from ...dependencies import get_embeddings
from ...services.vector_store_service import VectorStoreService

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/update")
async def update_vector_store(
    embeddings=Depends(get_embeddings)
):
    try:
        service = VectorStoreService(embeddings)
        await service.update_vector_store()
        return {"message": "Vector store updated successfully"}
    except Exception as e:
        logger.error(f"Error updating vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))