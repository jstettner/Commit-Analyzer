"""
Diff analyzer module that uses OpenAI's API to analyze git diffs.
"""
import os
from typing import Optional
from pathlib import Path
import openai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Configure OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class DiffAnalysis(BaseModel):
    """Model for structured diff analysis results"""
    summary: str = Field(description="High-level summary of changes")
    impact: str = Field(description="Potential impact of the changes")
    files_changed: list[str] = Field(description="List of modified files")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _analyze_with_llm(diff: str) -> DiffAnalysis:
    """
    Analyze a git diff using OpenAI's API with retry logic
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a code review assistant. Analyze the provided git diff and explain the changes, their potential impact, and any important considerations."
                },
                {
                    "role": "user",
                    "content": f"Please analyze this git diff and provide a structured response:\n\n{diff}"
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract changed files from diff
        files_changed = [
            line.split(" ")[1] 
            for line in diff.split("\n") 
            if line.startswith("diff --git")
        ]
        
        return DiffAnalysis(
            summary=response.choices[0].message.content.split("\n")[0],
            impact="\n".join(response.choices[0].message.content.split("\n")[1:]),
            files_changed=files_changed
        )
    except Exception as e:
        raise RuntimeError(f"Failed to analyze diff with LLM: {str(e)}")

def analyze_diff(diff: str) -> str:
    """
    Analyze a git diff and return a human-readable analysis
    
    Args:
        diff: The git diff to analyze
        
    Returns:
        A formatted string containing the analysis
    """
    try:
        analysis = _analyze_with_llm(diff)
        
        return f"""
Summary: {analysis.summary}

Impact and Considerations:
{analysis.impact}

Files Changed:
{chr(10).join(f'- {file}' for file in analysis.files_changed)}
""".strip()
    except Exception as e:
        return f"Error analyzing diff: {str(e)}"
