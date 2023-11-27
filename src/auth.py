from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import hashlib


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # In a real-world scenario, you would validate the token and retrieve user information from a database.
    # For simplicity, we'll just check if the token is a known username in our JSON file.
    with open(USERS_DB_PATH, "r") as file:
        users = json.load(file)
        for user in users:
            if user["username"] == token:
                return user
    raise credentials_exception