"""
Lucy Evaluator - Quality Control Assistant

ROLE:
Checks every response BEFORE returning to user

EVALUATION CRITERIA:
1. Relevance (90%+) - Does it answer the question?
2. Completeness (85%+) - All requested info included?
3. Accuracy (95%+) - Sources valid and recent?
4. Clarity (80%+) - Clear and well-structured?
5. Safety (100%) - No harmful content?

QUALITY THRESHOLD: 80% overall
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import os

app = FastAPI(title="Lucy Evaluator")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

class EvaluationRequest(BaseModel):
    query: str
    response: str
    agent: str
    sources: List[Dict]
    confidence: float

class EvaluationResponse(BaseModel):
    quality_score: float  # 0.0 - 1.0
    passed: bool  # True if >= 0.8
    issues: List[str]
    suggestions: List[str]
    reasoning: str

@app.get("/health")
async def health():
    return {"status": "healthy", "assistant": "evaluator"}

@app.post("/evaluate")
async def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    """
    Evaluate response quality
    
    Returns quality score (0-1) and pass/fail
    Provides suggestions if quality is low
    """
    
    # TODO: Use Claude to evaluate response
    # For now, simple heuristic
    
    issues = []
    suggestions = []
    
    # Check 1: Relevance (keywords match)
    if not any(word in request.response.lower() for word in request.query.lower().split()):
        issues.append("Response may not be relevant to query")
        suggestions.append("Ensure response directly addresses the query")
    
    # Check 2: Completeness (has sources)
    if not request.sources:
        issues.append("No sources provided")
        suggestions.append("Include sources to support claims")
    
    # Check 3: Accuracy (sources recent if date-sensitive)
    # TODO: Check source dates
    
    # Check 4: Clarity (not too short, not too long)
    word_count = len(request.response.split())
    if word_count < 10:
        issues.append("Response too brief")
        suggestions.append("Provide more detail")
    elif word_count > 500:
        issues.append("Response too verbose")
        suggestions.append("Be more concise")
    
    # Check 5: Safety
    # TODO: Check for harmful content
    
    # Calculate quality score
    base_score = request.confidence
    
    # Penalties
    if not request.sources:
        base_score -= 0.1
    if word_count < 10 or word_count > 500:
        base_score -= 0.05
    
    quality_score = max(0.0, min(1.0, base_score))
    
    return EvaluationResponse(
        quality_score=quality_score,
        passed=quality_score >= 0.8,
        issues=issues,
        suggestions=suggestions,
        reasoning=f"Evaluated based on relevance, completeness, clarity. Score: {quality_score:.2f}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
