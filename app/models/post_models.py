from pydantic import BaseModel
from typing import List

class LinkedInPostRequest(BaseModel):
    num_posts: int = 3
    custom_prompt: str | None = None

class LinkedInPost(BaseModel):
    content: str

class LinkedInPostResponse(BaseModel):
    posts: List[LinkedInPost]