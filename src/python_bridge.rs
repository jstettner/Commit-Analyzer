use anyhow::{Context, Result};
use std::path::Path;
use std::process::Command;
use std::env;
use std::fs;
use std::io::{BufReader, Read, Write};

/// Analyzes a git diff using the Python ML module
pub fn analyze_diff(diff: &str) -> Result<String> {
    let venv_python = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("venv")
        .join("bin")
        .join("python3");

    let module_path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("python_module");

    // Create a temporary file for the diff
    let temp_diff_path = module_path.join("temp_diff.txt");
    fs::write(&temp_diff_path, diff)
        .context("Failed to write diff to temporary file")?;

    let script = format!("\
from pathlib import Path
import sys
sys.path.append('{}')

from diff_analyzer import analyze_diff
with open('{}', 'r') as f:
    diff_content = f.read()

# Stream tokens as they are generated
for token in analyze_diff(diff_content):
    print(token, end='', flush=True)\
",
        module_path.display(),
        temp_diff_path.display()
    );

    let mut child = Command::new(&venv_python)
        .arg("-c")
        .arg(&script)
        .current_dir(&module_path)
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .context("Failed to spawn Python subprocess")?;

    let stdout = child.stdout.take().unwrap();
    let mut reader = BufReader::new(stdout);
    let mut buffer = [0; 1];

    // Stream output in real-time
    let mut result = String::new();
    while let Ok(n) = reader.read(&mut buffer) {
        if n == 0 { break; }
        print!("{}", String::from_utf8_lossy(&buffer[..n]));
        std::io::stdout().flush().ok();
        result.push_str(&String::from_utf8_lossy(&buffer[..n]));
    }

    // Wait for the process to complete
    let status = child.wait()
        .context("Failed to wait for Python subprocess")?;

    // Clean up temporary file
    let _ = fs::remove_file(temp_diff_path);

    if !status.success() {
        let mut stderr = String::new();
        if let Some(mut stderr_handle) = child.stderr {
            use std::io::Read;
            stderr_handle.read_to_string(&mut stderr).ok();
        }
        anyhow::bail!("Python subprocess failed: {}", stderr);
    }

    Ok(result)
}
