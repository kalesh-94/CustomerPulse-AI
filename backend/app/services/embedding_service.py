from app.services.model_loader import embedding_model

def generate_embeddings(texts):
    return embedding_model.encode(texts)