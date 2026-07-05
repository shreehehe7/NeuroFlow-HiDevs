from pydantic import BaseModel

class Document(BaseModel):
    id: str
    status: str

class QueryResult(BaseModel):
    answer: str

class EvaluationResult(BaseModel):
    overall_score: float
