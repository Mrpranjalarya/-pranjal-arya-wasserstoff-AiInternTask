from typing import List, Tuple
import nltk

# Ensure necessary NLTK tokenizers are downloaded once
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)


def chunk_text(text: str, doc_id: str, chunk_size: int = 500, overlap: int = 50) -> Tuple[List[str], List[str], List[dict]]:
    """
    Splits `text` into overlapping token-based chunks.
    Returns: chunk_texts, chunk_ids, metadata_list.
    Metadata includes doc_id, start_char, end_char.
    """
    tokens = nltk.word_tokenize(text)
    chunks, ids, meta = [], [], []
    i = 0
    while i < len(tokens):
        chunk_tokens = tokens[i : i + chunk_size]
        chunk_text = " ".join(chunk_tokens)
        # Calculate character offsets for metadata
        start_char = sum(len(t) + 1 for t in tokens[:i])  # +1 for spaces
        end_char = start_char + len(chunk_text)
        chunk_id = f"{doc_id}_{i}"

        chunks.append(chunk_text)
        ids.append(chunk_id)
        meta.append({
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "start": start_char,
            "end": end_char
        })

        i += chunk_size - overlap
    return chunks, ids, meta
