from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


load_dotenv()
db_url = os.environ["QDRANT_URL"]
collection_name = os.environ["COLLECTION_NAME"]

client = QdrantClient(url=db_url)
model = SentenceTransformer(
     "dunzhang/stella_en_400M_v5",
     trust_remote_code=True,
     device="cpu",
     config_kwargs={"use_memory_efficient_attention": False, "unpad_inputs": False}
 )

def generate_embedding(query):
    embeddings = model.encode(query).tolist()
    return embeddings

def format_retrieved_snippets(snippets):
    formatted_snippets = ""
    for i, snippet in enumerate(snippets):
        query = snippet["query"]
        code = snippet["code"]
        formatted_snippets += f" Snippet {i + 1} (Query: {query}):\n```\n{code}\n```\n\n"
    return formatted_snippets

def get_relevant_snippets(query):
    result = client.query_points(
        collection_name=collection_name,
        query = generate_embedding(query),
        with_payload=["query", "code"],
        limit=3
    ).points
    snippets = [point.payload for point in result]
    formatted_snippets = format_retrieved_snippets(snippets)
    return formatted_snippets

if __name__ == "__main__":
  pass
