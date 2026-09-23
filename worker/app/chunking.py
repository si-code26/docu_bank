import tiktoken

ENCODING=tiktoken.get_encoding("cl100k_base")
CHUNK_TOKENS=500
OVERLAP_TOKENS=60

def chunk_text(text: str) -> list[str]:
    tokens = ENCODING.encode(text)
    
    if len(tokens) <= CHUNK_TOKENS:
        return [text] if text.strip() else []

    chunks: list[str] = []
    step = CHUNK_TOKENS - OVERLAP_TOKENS

    for start in range(0, len(tokens), step):
       piece = tokens[start:start+CHUNK_TOKENS]
       chunks.append(ENCODING.decode(piece))
       if start + CHUNK_TOKENS >= len(tokens):
            break

    return chunks
