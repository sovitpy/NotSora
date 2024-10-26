import json
import time
from sentence_transformers import SentenceTransformer 
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os
from dotenv import load_dotenv
import pickle

load_dotenv()
db_url = os.environ["QDRANT_URL"]
collection_name = os.environ["COLLECTION_NAME"]

model = SentenceTransformer(
     "dunzhang/stella_en_400M_v5",
     trust_remote_code=True,
     device="cpu",
     config_kwargs={"use_memory_efficient_attention": False, "unpad_inputs": False}
 )

with open('manim_queries.json', 'r') as f:
    data = json.loads(f.read())

queries = list(pair['query'].replace('\n', '') for pair in data)
code = list(pair['answer'] for pair in data)
embeddings = model.encode(queries, show_progress_bar = True)
embeddings = [emb.tolist() for emb in embeddings]

# Saving embeddings in case qdrant crashes.
with open('embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

# Load the embeddings from the file
#with open('embeddings.pkl', 'rb') as f:
#    embeddings = pickle.load(f)


client = QdrantClient(url=db_url, timeout=500)
qdrant_points = []
for i in range(len(queries)):
    print(f"Populating query: {queries[i]} {i+1}/{len(queries)}\n")
    qdrant_points.append(PointStruct(
        vector = embeddings[i],
        id = i,
        payload = {
            "code": code[i],
            "query": queries[i]
        }
    ))
operation_info = client.upsert(collection_name = collection_name,
                            wait=True,
                               points = qdrant_points)
print(operation_info)
