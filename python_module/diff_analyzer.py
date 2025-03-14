"""
Diff analyzer module that uses OpenAI's API to analyze git diffs.
"""
import os
import sys
import logging
from typing import Optional
from pathlib import Path
import openai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, before_log, after_log, retry_if_exception_type
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = openai.OpenAI(api_key=api_key)

class DiffAnalysis(BaseModel):
    """Model for structured diff analysis results"""
    summary: str = Field(description="High-level summary of changes")
    impact: str = Field(description="Potential impact of the changes")
    files_changed: list[str] = Field(description="List of modified files")

def _analyze_with_llm(diff: str) -> DiffAnalysis:
    """
    Analyze a git diff using OpenAI's API and stream the response
    """
    if not diff.strip():
        raise ValueError("Empty diff provided")

    try:
        logger.info("Sending diff to OpenAI API for analysis")
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "developer",
                    "content": "You are a code review assistant. Analyze the provided git diff and explain the changes, their potential impact, and any important considerations. Focus on the key changes and their implications."
                },
                {
                    "role": "user",
                    "content": f"Please analyze this git diff and provide a structured, terminal-friendly response:\n\n{diff}"
                }
            ],
            temperature=0.3,
            max_tokens=2048,
            stream=True
        )
        
        # Extract changed files from diff
        files_changed = [
            line.split(" ")[2][2:]
            for line in diff.split("\n") 
            if line.startswith("diff --git")
        ]
        
        # Stream and collect the response
        content = ""
        print("Analysis:", end="", flush=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                content += token
                print(token, end="", flush=True)
        print()  # New line after streaming completes
        
        summary_lines = content.split("\n")
        
        return DiffAnalysis(
            summary=summary_lines[0],
            impact="\n".join(summary_lines[1:]) if len(summary_lines) > 1 else "No additional impact details provided",
            files_changed=files_changed
        )
    except openai.RateLimitError as e:
        logger.error(f"OpenAI API rate limit exceeded: {str(e)}. Retrying with exponential backoff...")
        raise
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise RuntimeError(f"OpenAI API error: {str(e)}. Please check your API key and permissions.")
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise RuntimeError(f"Failed to analyze diff: {str(e)}")

def analyze_diff(diff: str) -> str:
    """
    Analyze a git diff and return a human-readable analysis
    
    Args:
        diff: The git diff to analyze
        
    Returns:
        A formatted string containing the analysis
    """
    try:
        logger.info("Starting diff analysis")
        analysis = _analyze_with_llm(diff)
        
        result = f"""
Summary: {analysis.summary}

Impact and Considerations:
{analysis.impact}

Files Changed:
{chr(10).join(f'- {file}' for file in analysis.files_changed)}
""".strip()
        logger.info("Analysis completed successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to analyze diff: {str(e)}")
        return f"Error analyzing diff: {str(e)}"
