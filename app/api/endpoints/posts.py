import logging
from fastapi import APIRouter, Depends, HTTPException
import aiohttp
from ...dependencies import get_embeddings, get_llm, get_async_session
from ...models.post_models import LinkedInPostRequest, LinkedInPostResponse
from ...services.post_service import PostGeneratorService

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=LinkedInPostResponse)
async def generate_posts(
    request: LinkedInPostRequest,
    embeddings=Depends(get_embeddings),
    llm=Depends(get_llm),
    session: aiohttp.ClientSession = Depends(get_async_session)
):
    try:
        service = PostGeneratorService(embeddings, llm, session)
        posts = await service.generate_posts(
            request.num_posts,
            request.custom_prompt
        )
        return LinkedInPostResponse(posts=posts)
    except Exception as e:
        logger.error(f"Error generating posts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))