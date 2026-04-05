from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text):
    embedding = model.encode(text)
    return embedding.tolist()

if __name__ == "__main__":
    result = embed_text("Database connection failed")
    print(type(result))
    print(len(result))
    print(result[:5])  # print first 5 numbers