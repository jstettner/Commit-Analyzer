# Halidom Brain - Git Commit Analyzer

A powerful tool that combines Rust and Python to analyze git commits using LLM technology. The tool extracts commit diffs and provides intelligent analysis of code changes.

## Features

- Git repository and commit validation
- Diff extraction and analysis
- LLM-powered commit understanding
- Clean separation between Rust CLI and Python ML components
- Robust error handling and logging

## Prerequisites

- Rust (latest stable)
- Python 3.8+
- Git
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd halidom-brain
```

2. Set up Python environment:
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r python_module/requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file in the project root
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

4. Build the Rust project:
```bash
cargo build --release
```

## Usage

```bash
# Basic usage
cargo run -- --commit <commit-hash> --directory <path-to-repo>

# Example
cargo run -- --commit abc123 --directory /path/to/repo
```

## Output

The tool provides:
- A summary of the changes
- Analysis of potential impact
- List of modified files

## Error Handling

The tool handles various error cases:
- Invalid repository paths
- Non-existent commit hashes
- LLM API failures
- Invalid UTF-8 in diffs

## Development

The project structure:
```
halidom-brain/
├── src/
│   ├── main.rs        # CLI implementation
│   ├── git.rs         # Git operations
│   └── python_bridge.rs # PyO3 bridge
├── python_module/
│   ├── diff_analyzer.py  # LLM integration
│   └── requirements.txt  # Python dependencies
└── Cargo.toml         # Rust dependencies
```
