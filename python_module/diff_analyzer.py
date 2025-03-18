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

def _analyze_with_llm(diff: str):
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
        
        # Stream the response
        content = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                content += token
                yield token
        
        # Yield files changed section
        yield "\n\nFiles Changed:\n"
        for file in files_changed:
            yield f"- {file}\n"
            
    except openai.RateLimitError as e:
        error_msg = f"OpenAI API rate limit exceeded: {str(e)}. Retrying with exponential backoff..."
        logger.error(error_msg)
        yield error_msg
    except openai.APIError as e:
        error_msg = f"OpenAI API error: {str(e)}. Please check your API key and permissions."
        logger.error(error_msg)
        yield error_msg
    except Exception as e:
        error_msg = f"Failed to analyze diff: {str(e)}"
        logger.error(error_msg)
        yield error_msg

def analyze_diff(diff: str):
    """
    Analyze a git diff and yield tokens as they are generated
    
    Args:
        diff: The git diff to analyze
        
    Yields:
        Tokens from the analysis as they are generated
    """
    try:
        logger.info("Starting diff analysis")
        yield "Analysis:\n"
        for token in _analyze_with_llm(diff):
            yield token
        logger.info("Analysis completed successfully")
    except Exception as e:
        error_msg = f"Error analyzing diff: {str(e)}"
        logger.error(error_msg)
        yield error_msg
