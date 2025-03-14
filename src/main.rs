use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use std::path::PathBuf;
use tracing::info;

mod git;
mod python_bridge;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Analyze git diff
    D {
        /// Git commit hash to analyze
        #[arg(short, long)]
        commit: String,

        /// Path to git repository
        #[arg(short, long)]
        directory: PathBuf,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    info!("Starting halidom commit analyzer");

    // Parse command line arguments
    let cli = Cli::parse();

    match cli.command {
        Commands::D { commit, directory } => {
            // Validate git repository and commit
            let repo_path = directory.canonicalize()
                .context("Failed to resolve repository path")?;
            
            git::validate_repository(&repo_path)
                .context("Failed to validate git repository")?;
            
            git::validate_commit(&repo_path, &commit)
                .context("Failed to validate commit hash")?;

            // Extract diff from commit
            let diff = git::get_commit_diff(&repo_path, &commit)
                .context("Failed to extract commit diff")?;

            // Initialize Python bridge and analyze diff
            let analysis = python_bridge::analyze_diff(&diff)
                .context("Failed to analyze diff using LLM")?;

            // Display results
            println!("\nCommit Analysis:\n{}", analysis);
        }
    }
    
    Ok(())
}
