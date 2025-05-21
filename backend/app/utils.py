from pathlib import Path
from app.config import settings

def list_vector_dbs() -> list[str]:
    """List all saved vector database directories ending with '_vec' in the data directory."""
    data_dir = Path(settings.DATA_DIR)
    if not data_dir.exists():
        return []
    return [p.name for p in data_dir.iterdir() if p.is_dir() and p.name.endswith("_vec")]
