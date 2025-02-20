import logging
import hashlib
import aiofiles
from typing import Dict

logger = logging.getLogger(__name__)

async def calculate_file_hash(file_path: str) -> str:
    """Calculate the SHA256 hash of a file asynchronously."""
    hash_obj = hashlib.sha256()
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(8192):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

async def load_existing_hashes(file_path: str) -> Dict[str, str]:
    """Load existing file hashes from a file asynchronously."""
    logger.info("Loading existing hashes from file: %s", file_path)
    hashes = {}
    try:
        async with aiofiles.open(file_path, 'r') as f:
            async for line in f:
                parts = line.strip().rsplit(" ", 1)
                if len(parts) == 2:
                    key, value = parts
                    hashes[key] = value
        logger.info("Loaded %d hashes from file: %s", len(hashes), file_path)
    except FileNotFoundError:
        logger.warning("%s not found, starting with an empty hash list.", file_path)
    return hashes

async def save_file_hashes(hashes: Dict[str, str], file_path: str) -> None:
    """Save updated file hashes to the hash store asynchronously."""
    logger.info("Saving %d file hashes to file: %s", len(hashes), file_path)
    async with aiofiles.open(file_path, "w") as f:
        for file_name, file_hash in hashes.items():
            await f.write(f"{file_name} {file_hash}\n")
    logger.info("Saved file hashes to file: %s", file_path)
