"""Pydantic models for API requests and responses."""
from pydantic import BaseModel

class ColumnSchema(BaseModel):
    column: str
    type: str

class UploadResponse(BaseModel):
    dataset_id: str
    table_name: str
    schema: list[ColumnSchema]
    row_count: int
    message: str

class AskRequest(BaseModel):
    dataset_id: str
    question: str

class AskResponse(BaseModel):
    answer: str
    sql_query: str
    data: list[dict]
    message: str
