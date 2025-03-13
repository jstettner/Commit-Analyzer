use anyhow::{Context, Result};
use std::path::Path;
use std::process::Command;

/// Validates that the given path is a git repository
pub fn validate_repository(path: &Path) -> Result<()> {
    let output = Command::new("git")
        .arg("rev-parse")
        .arg("--git-dir")
        .current_dir(path)
        .output()
        .context("Failed to execute git command")?;

    if !output.status.success() {
        anyhow::bail!("Directory is not a valid git repository");
    }

    Ok(())
}

/// Validates that the given commit hash exists in the repository
pub fn validate_commit(repo_path: &Path, commit_hash: &str) -> Result<()> {
    let output = Command::new("git")
        .args(["cat-file", "-e", &format!("{}^{{commit}}", commit_hash)])
        .current_dir(repo_path)
        .output()
        .context("Failed to execute git command")?;

    if !output.status.success() {
        anyhow::bail!("Invalid or non-existent commit hash");
    }

    Ok(())
}

/// Gets the diff for a specific commit
pub fn get_commit_diff(repo_path: &Path, commit_hash: &str) -> Result<String> {
    let output = Command::new("git")
        .args(["show", "--patch", commit_hash])
        .current_dir(repo_path)
        .output()
        .context("Failed to execute git show command")?;

    if !output.status.success() {
        anyhow::bail!("Failed to get commit diff");
    }

    String::from_utf8(output.stdout)
        .context("Failed to parse git diff output as UTF-8")
}
