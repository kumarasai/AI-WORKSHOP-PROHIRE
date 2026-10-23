
import os

import instructor
from dotenv import load_dotenv
from groq import Groq
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationError,
    field_validator,
)

import re


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Check your .env file."
    )

# Define the structured output schema
class UserProfile(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=18, le=120)
    email: EmailStr
    pan: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        value = value.strip().upper()

        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):
            raise ValueError("Invalid PAN format")

        return value


# Initialize Groq
groq_client = Groq(api_key=api_key)

# Wrap the Groq client with Instructor
client = instructor.from_groq(
    groq_client,
    mode=instructor.Mode.TOOLS,
)

try:
    profile = client.chat.completions.create(
        model=model,
        response_model=UserProfile,
        messages=[
            {
                "role": "system",
                "content": (
                    "Generate a fictional user profile. "
                    "Use fictional data only. "
                    "The email must be an example.com address. "
                    "The PAN must be a clearly fictional "
                    "test value matching the required format. "
                    "Never use actual personal information."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Create a fictional profile for an adult "
                    "user with a name, age, email and PAN-format "
                    "test identifier."
                ),
            },
        ],
        max_retries=2,
    )

    # Instructor returns a validated Pydantic object
    print("Structured JSON response:")
    print(profile.model_dump_json(indent=2))

    print("\nValidation successful:", isinstance(profile, UserProfile))

except ValidationError as exc:
    print("The response did not pass validation:")
    print(exc)

except Exception as exc:
    print("The Groq / Instructor request failed:")
    print(f"{type(exc).__name__}: {exc}")