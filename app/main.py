from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from .dependencies import get_embeddings, get_llm, get_async_session
from .models import LinkedInPostRequest, LinkedInPostResponse
from .services import PostGeneratorService

app = FastAPI(
    title="LinkedIn Post Generator API",
    description="An async API that generates LinkedIn posts based on provided PDF documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-posts/", response_model=LinkedInPostResponse)
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
        raise HTTPException(status_code=500, detail=str(e))
