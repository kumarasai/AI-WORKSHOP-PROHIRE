import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ValidationError,
    field_validator,
)


class UserProfile(BaseModel):
    name: str = Field(
        min_length=1,
        description="User's full name",
    )

    age: int = Field(
        ge=18,
        le=120,
        description="User's age",
    )

    email: EmailStr

    pan: str = Field(
        description="Indian PAN identifier",
    )

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
            raise ValueError(
                "PAN must contain 5 letters, 4 digits, "
                "and 1 letter"
            )

        return value


if __name__ == "__main__":
    # Example of valid, fictional test data
    valid_data = {
        "name": "Test User",
        "age": 25,
        "email": "test.user@example.com",
        "pan": "ABCDE1234F",
    }

    profile = UserProfile(**valid_data)

    print("Valid profile:")
    print(profile.model_dump_json(indent=2))

    # Deliberately invalid data
    invalid_data = {
        "name": "   ",
        "age": 15,
        "email": "not-an-email",
        "pan": "ABC123",
    }

    print("\nTesting invalid profile:")

    try:
        UserProfile(**invalid_data)
    except ValidationError as exc:
        print("Validation failed:")
        print(exc)