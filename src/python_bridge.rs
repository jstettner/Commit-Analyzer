use anyhow::{Context, Result};
use std::path::Path;
use std::process::Command;
use std::env;
use std::fs;

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
print(analyze_diff(diff_content))\
", 
        module_path.display(),
        temp_diff_path.display()
    );

    let output = Command::new(&venv_python)
        .arg("-c")
        .arg(&script)
        .current_dir(&module_path)
        .output()
        .context("Failed to execute Python subprocess")?;

    // Clean up temporary file
    let _ = fs::remove_file(temp_diff_path);

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        anyhow::bail!("Python subprocess failed: {}", error);
    }

    String::from_utf8(output.stdout)
        .context("Failed to parse Python output as UTF-8")
}
