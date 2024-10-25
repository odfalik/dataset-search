import openai
from pinecone import Pinecone
import tiktoken
from api.config import settings

# OpenAI
openai.api_key = settings.OPENAI_API_KEY
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

EMBEDDING_MODEL = "text-embedding-ada-002"
ada_002_encoding = tiktoken.encoding_for_model(EMBEDDING_MODEL)

# Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)
