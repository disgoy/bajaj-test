import os
import re
from typing import Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env file

app = FastAPI()

class DataIn(BaseModel):
    data: List[Any]  # accept numbers/strings; we'll coerce to str

def build_user_id() -> str:
    # Set these via environment variables when you deploy (or change defaults here)
    full_name = os.getenv("FULL_NAME", "john_doe").strip().lower().replace(" ", "_")
    dob = os.getenv("DOB_DDMMYYYY", "17091999").strip()  # ddmmyyyy
    return f"{full_name}_{dob}"

@app.post("/bfhl")
def bfhl(payload: DataIn):
    # Validate & normalize input
    try:
        items = [str(x).strip() for x in payload.data]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid 'data' array.")

    odd_numbers: List[str] = []
    even_numbers: List[str] = []
    alphabets: List[str] = []
    special_characters: List[str] = []
    total = 0

    # Collect *all* alphabetical characters from the entire input (for concat_string)
    letters: List[str] = []

    for token in items:
        # Numbers: strictly digits with optional leading '-' (returned as strings)
        if re.fullmatch(r"-?\d+", token):
            n = int(token)
            total += n
            (even_numbers if n % 2 == 0 else odd_numbers).append(token)
        # Alphabets: only letters (convert whole token to uppercase for output)
        elif re.fullmatch(r"[A-Za-z]+", token):
            alphabets.append(token.upper())
            letters.extend(list(token))
        else:
            # Everything else = "special characters" bucket (as given)
            special_characters.append(token)
            # Still harvest any letters inside mixed tokens for concat_string
            letters.extend([ch for ch in token if ch.isalpha()])

    # Build concat_string:
    # 1) reverse all collected letters,
    # 2) apply alternating caps starting with UPPER at index 0
    letters_rev = list(reversed(letters))
    alt_caps = [ch.upper() if i % 2 == 0 else ch.lower() for i, ch in enumerate(letters_rev)]
    concat_string = "".join(alt_caps)

    return {
        "is_success": True,  # status flag the paper asks for
        "user_id": build_user_id(),  # format: full_name_ddmmyyyy in lowercase
        "email": os.getenv("EMAIL", "you@example.com"),
        "roll_number": os.getenv("ROLL_NUMBER", "ABCD123"),
        "odd_numbers": odd_numbers,              # numbers returned as strings
        "even_numbers": even_numbers,            # numbers returned as strings
        "alphabets": alphabets,                  # tokens of letters, uppercased
        "special_characters": special_characters,
        "sum": str(total),                       # sum returned as a string
        "concat_string": concat_string
    }
