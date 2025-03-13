use anyhow::{Context, Result};
use clap::Parser;
use std::path::PathBuf;
use tracing::info;

mod git;
mod python_bridge;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Git commit hash to analyze
    #[arg(short, long)]
    commit: String,

    /// Path to git repository
    #[arg(short, long)]
    directory: PathBuf,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    info!("Starting halidom-brain commit analyzer");

    // Parse command line arguments
    let args = Args::parse();

    // Validate git repository and commit
    let repo_path = args.directory.canonicalize()
        .context("Failed to resolve repository path")?;
    
    git::validate_repository(&repo_path)
        .context("Failed to validate git repository")?;
    
    git::validate_commit(&repo_path, &args.commit)
        .context("Failed to validate commit hash")?;

    // Extract diff from commit
    let diff = git::get_commit_diff(&repo_path, &args.commit)
        .context("Failed to extract commit diff")?;

    // Initialize Python bridge and analyze diff
    let analysis = python_bridge::analyze_diff(&diff)
        .context("Failed to analyze diff using LLM")?;

    // Display results
    println!("\nCommit Analysis:\n{}", analysis);
    
    Ok(())
}
