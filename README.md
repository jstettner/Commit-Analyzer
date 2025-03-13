# Halidom Brain - Git Commit Analyzer

A powerful tool that combines Rust and Python to analyze git commits using LLM technology. The tool extracts commit diffs and provides intelligent analysis of code changes, helping teams understand the impact and implications of their code modifications.

## Features

- Git repository and commit validation
- Intelligent diff extraction and analysis
- LLM-powered commit understanding using OpenAI's API
- Clean separation between Rust CLI and Python ML components
- Robust error handling with automatic retries
- Comprehensive logging for debugging

## Prerequisites

- Rust (latest stable)
- Python 3.8+
- Git
- OpenAI API key (get one at https://platform.openai.com/api-keys)

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
# Copy the environment template
cp .env.template .env

# Edit .env and add your OpenAI API key
# IMPORTANT: Never commit your .env file or share your API key
```

4. Build the Rust project:
```bash
cargo build --release
```

## Usage

```bash
# Basic usage
cargo run -- --commit <commit-hash> --directory <path-to-repo>

# Example: Analyze the latest commit in current directory
cargo run -- --commit HEAD --directory .

# Example: Analyze a specific commit
cargo run -- --commit abc123 --directory /path/to/repo
```

## Output

The tool provides structured analysis including:
- A detailed summary of the changes
- Analysis of potential impact and considerations
- List of modified files with their significance
- Suggestions for testing and deployment

Example output:
```
Summary: Implement user authentication system

Impact and Considerations:
- Adds secure password hashing with bcrypt
- Introduces session management
- Updates database schema
- Requires database migration before deployment

Files Changed:
- src/auth.rs
- src/models/user.rs
- migrations/001_create_users.sql
```

## Error Handling

The tool handles various error cases with grace:
- Invalid repository paths or commit hashes
- OpenAI API rate limits and errors (with automatic retries)
- Invalid UTF-8 in diffs
- Python environment issues
- File system access problems

When encountering errors:
1. Check your OpenAI API key in `.env`
2. Ensure the Python virtual environment is activated
3. Verify the git repository and commit exist
4. Check the logs for detailed error messages

## Security

- Never commit your `.env` file
- Keep your OpenAI API key secure
- The `.gitignore` is configured to prevent accidental commits of sensitive files
- Use environment variables for all sensitive configuration

## Development

The project structure:
```
halidom-brain/
├── src/                    # Rust source code
│   ├── main.rs            # CLI implementation
│   ├── git.rs             # Git operations
│   └── python_bridge.rs   # Python integration
├── python_module/         # Python ML components
│   ├── diff_analyzer.py   # LLM integration
│   └── requirements.txt   # Python dependencies
├── .env.template          # Environment template
└── .gitignore            # Git ignore patterns
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Ensure your changes include:
- Appropriate error handling
- Logging for important operations
- Documentation updates
- Security considerations

## License

[Add your license information here]
