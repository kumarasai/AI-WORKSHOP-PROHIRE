import os

from dotenv import load_dotenv
from groq import AuthenticationError, Groq, NotFoundError

# Load the local .env file
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add your Groq API key to the .env file as: GROQ_API_KEY=gsk_..."
    )

if not api_key.startswith("gsk_"):
    raise RuntimeError(
        "GROQ_API_KEY is not a valid Groq API key. Get a new key from the Groq Console and paste it in .env as GROQ_API_KEY=gsk_..."
    )

# Initialize the Groq client
client = Groq(api_key=api_key)

try:
    # Send a request to the cloud LLM
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Reply with: Groq API connection successful!"
            }
        ],
        temperature=0,
        max_tokens=50,
    )
except AuthenticationError as exc:
    raise RuntimeError(
        "Authentication failed. Your Groq API key is invalid or expired. Generate a new key in the Groq Console and update .env."
    ) from exc
except NotFoundError as exc:
    raise RuntimeError(
        f"Model '{model}' is not available for this Groq account. "
        "Use a supported model such as 'openai/gpt-oss-20b' or 'qwen/qwen3.8-27b' by setting GROQ_MODEL in .env."
    ) from exc

print(response.choices[0].message.content)