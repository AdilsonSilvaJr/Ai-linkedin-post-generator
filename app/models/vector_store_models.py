from pydantic import BaseModel
from typing import Dict

class VectorStoreStatus(BaseModel):
    total_documents: int
    collection_name: str
    files_processed: Dict[str, str]