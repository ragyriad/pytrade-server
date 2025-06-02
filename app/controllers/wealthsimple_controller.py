from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.wealthsimple_service import WealthsimpleAPI
from app.database.connection import get_db
