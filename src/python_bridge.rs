use anyhow::{Context, Result};
use std::path::Path;
use std::process::Command;
use std::env;

/// Analyzes a git diff using the Python ML module
pub fn analyze_diff(diff: &str) -> Result<String> {
    let venv_python = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("venv")
        .join("bin")
        .join("python3");

    let module_path = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("python_module");

    let output = Command::new(venv_python)
        .arg("-c")
        .arg(format!("\
from pathlib import Path

import sys
sys.path.append('{}')

from diff_analyzer import analyze_diff
print(analyze_diff(r'''{}'''))\
", module_path.display(), diff))
        .output()
        .context("Failed to execute Python script")?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        anyhow::bail!("Python script failed: {}", error);
    }

    String::from_utf8(output.stdout)
        .context("Failed to parse Python output as UTF-8")
}
