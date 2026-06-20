from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import GOOGLE_API_KEY, GEMINI_MODEL

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3,
)
