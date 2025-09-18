# Quick test with smaller model
from sentence_transformers import SentenceTransformer

# Use smaller, faster model (20MB vs 90MB)
model = SentenceTransformer('all-MiniLM-L12-v2')
print("Model loaded successfully!")

# Test embedding
text = "This is a test sentence"
embedding = model.encode([text])
print(f"Embedding shape: {embedding.shape}")