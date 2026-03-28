"""
Azure OpenAI API with Function Calling and Structured Output
- /chat: Function calling for datetime and calculations
- /generate/mcq: Generate multiple choice questions
- /generate/essay: Generate essay questions
"""

import json
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv()

from client import client, deployment_name
from function_calling import chat_with_functions
from structured_output import mcq_schema, essay_generation_schema


app = FastAPI(
    title="Azure OpenAI API",
    description="Function Calling & Structured Output with Azure OpenAI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ REQUEST/RESPONSE MODELS ============

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message (datetime or math questions)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "What time is it?"},
                {"message": "Calculate 25 * 4 + 10"},
                {"message": "What day is today and what's 2^10?"}
            ]
        }
    }


class ChatResponse(BaseModel):
    response: str


class QuizRequest(BaseModel):
    topic: str = Field(..., description="Topic for question generation")
    num_questions: int = Field(default=5, ge=1, le=20, description="Number of questions (1-20)")
    difficulty: Optional[str] = Field(default="medium", description="Difficulty: easy, medium, hard")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"topic": "Python programming", "num_questions": 5, "difficulty": "medium"},
                {"topic": "World War II history", "num_questions": 3, "difficulty": "hard"}
            ]
        }
    }


class MCQItem(BaseModel):
    id: str
    question: str
    options: list[str]
    answer_index: int
    explanation: str


class MCQResponse(BaseModel):
    topic: str
    difficulty: str
    requested: int
    returned: int
    questions: list[MCQItem]


class EssayItem(BaseModel):
    id: str
    question: str
    explanation: str


class EssayResponse(BaseModel):
    topic: str
    difficulty: str
    requested: int
    returned: int
    questions: list[EssayItem]


# ============ ENDPOINTS ============

@app.get("/", tags=["Home"])
async def index():
    return {
        "message": "Azure OpenAI API - Function Calling & Structured Output",
        "endpoints": {
            "/chat": "POST - Function calling (datetime, calculations)",
            "/generate/mcq": "POST - Generate multiple choice questions",
            "/generate/essay": "POST - Generate essay questions"
        }
    }


@app.post("/chat", response_model=ChatResponse, tags=["Function Calling"])
async def chat(request: ChatRequest):
    """
    Chat with function calling support.
    
    Supports:
    - Datetime queries: "What time is it?", "What's today's date?"
    - Math calculations: "Calculate 25 * 4", "What's the square root of 144?"
    """
    try:
        response = chat_with_functions(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/mcq", response_model=MCQResponse, tags=["Quiz Generation"])
async def generate_mcq(request: QuizRequest):
    """
    Generate multiple choice questions on a given topic.
    
    - Each question has 4 options with one correct answer
    - Returns answer_index (0-3) and explanation
    - Results filtered to match requested num_questions
    """
    try:
        prompt = f"""Generate exactly {request.num_questions} multiple choice questions about: {request.topic}

Difficulty level: {request.difficulty}

Requirements:
- Each question should have exactly 4 options
- Options should be plausible and well-crafted
- Include clear explanations for the correct answer
- Make questions progressively varied in sub-topics
- Use unique IDs like q1, q2, q3, etc."""

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert quiz generator. Generate high-quality multiple choice questions with clear, educational explanations."},
                {"role": "user", "content": prompt}
            ],
            response_format=mcq_schema
        )

        result = json.loads(response.choices[0].message.content)
        questions = result.get("questions", [])
        
        # Filter to requested number
        questions = questions[:request.num_questions]
        
        return MCQResponse(
            topic=request.topic,
            difficulty=request.difficulty,
            requested=request.num_questions,
            returned=len(questions),
            questions=[MCQItem(**q) for q in questions]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/essay", response_model=EssayResponse, tags=["Quiz Generation"])
async def generate_essay(request: QuizRequest):
    """
    Generate essay/open-ended questions on a given topic.
    
    - Each question includes a model answer/explanation
    - Suitable for study guides or assessment rubrics
    - Results filtered to match requested num_questions
    """
    try:
        prompt = f"""Generate exactly {request.num_questions} essay-style questions about: {request.topic}

Difficulty level: {request.difficulty}

Requirements:
- Questions should require thoughtful, detailed responses
- Provide comprehensive model answers/explanations
- Cover different aspects of the topic
- Use unique IDs like q1, q2, q3, etc."""

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert educator. Generate thought-provoking essay questions with comprehensive model answers suitable for study and assessment."},
                {"role": "user", "content": prompt}
            ],
            response_format=essay_generation_schema
        )

        result = json.loads(response.choices[0].message.content)
        questions = result.get("questions", [])
        
        # Filter to requested number
        questions = questions[:request.num_questions]
        
        return EssayResponse(
            topic=request.topic,
            difficulty=request.difficulty,
            requested=request.num_questions,
            returned=len(questions),
            questions=[EssayItem(**q) for q in questions]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

