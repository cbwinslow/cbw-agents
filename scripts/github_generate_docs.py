#!/usr/bin/env python3
"""
GitHub Bulk Documentation Generator

Generate comprehensive documentation for all repositories in a GitHub account.
Creates README files, API documentation, architecture diagrams, and more.

Usage:
    python scripts/github_generate_docs.py USERNAME
    python scripts/github_generate_docs.py USERNAME --output-dir ./docs
    python scripts/github_generate_docs.py USERNAME --include-diagrams --include-api-docs
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.github_operations import GitHubOperationsTool


def generate_repository_overview(repo: Dict, repo_dir: Path) -> None:
    """Generate overview documentation for a repository."""
    output_file = repo_dir / "OVERVIEW.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# {repo['name']}\n\n")
        
        if repo.get('description'):
            f.write(f"{repo['description']}\n\n")
        
        f.write("## Repository Information\n\n")
        f.write(f"- **Full Name:** {repo['full_name']}\n")
        f.write(f"- **Owner:** {repo['owner']['login']}\n")
        f.write(f"- **URL:** {repo['html_url']}\n")
        f.write(f"- **Clone URL:** `{repo['clone_url']}`\n")
        f.write(f"- **Default Branch:** {repo['default_branch']}\n")
        f.write(f"- **Visibility:** {'Private' if repo['private'] else 'Public'}\n\n")
        
        f.write("## Statistics\n\n")
        f.write(f"- **Stars:** ⭐ {repo['stargazers_count']:,}\n")
        f.write(f"- **Forks:** 🍴 {repo['forks_count']:,}\n")
        f.write(f"- **Watchers:** 👁 {repo['watchers_count']:,}\n")
        f.write(f"- **Open Issues:** {repo['open_issues_count']}\n")
        f.write(f"- **Size:** {repo['size']} KB\n\n")
        
        f.write("## Timeline\n\n")
        f.write(f"- **Created:** {repo['created_at'][:10]}\n")
        f.write(f"- **Last Updated:** {repo['updated_at'][:10]}\n")
        f.write(f"- **Last Push:** {repo['pushed_at'][:10]}\n\n")
        
        if repo.get('language'):
            f.write(f"## Primary Language\n\n")
            f.write(f"{repo['language']}\n\n")
        
        if repo.get('topics'):
            f.write("## Topics\n\n")
            for topic in repo['topics']:
                f.write(f"- {topic}\n")
            f.write("\n")
        
        if repo.get('homepage'):
            f.write(f"## Homepage\n\n")
            f.write(f"{repo['homepage']}\n\n")


def generate_file_structure_doc(tree_data: Dict, repo_dir: Path) -> None:
    """Generate file structure documentation."""
    if not tree_data or 'tree' not in tree_data:
        return
    
    output_file = repo_dir / "FILE_STRUCTURE.md"
    
    with open(output_file, 'w') as f:
        f.write("# File Structure\n\n")
        f.write("## Directory Tree\n\n")
        f.write("```\n")
        
        # Organize files by directory
        dirs = {}
        files = []
        
        for item in tree_data['tree']:
            if item['type'] == 'tree':
                dirs[item['path']] = item
            else:
                files.append(item)
        
        # Write directories
        for dir_path in sorted(dirs.keys()):
            f.write(f"📁 {dir_path}/\n")
        
        # Write files
        for file in sorted(files, key=lambda x: x['path']):
            path_parts = file['path'].split('/')
            indent = "  " * (len(path_parts) - 1)
            f.write(f"{indent}📄 {path_parts[-1]}\n")
        
        f.write("```\n\n")
        
        # Statistics
        f.write("## Statistics\n\n")
        f.write(f"- **Total Directories:** {len(dirs)}\n")
        f.write(f"- **Total Files:** {len(files)}\n")
        f.write(f"- **Total Items:** {len(tree_data['tree'])}\n\n")
        
        # File types
        extensions = {}
        for file in files:
            ext = Path(file['path']).suffix or 'no_extension'
            extensions[ext] = extensions.get(ext, 0) + 1
        
        if extensions:
            f.write("## File Types\n\n")
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{ext}**: {count} files\n")


def generate_language_analysis_doc(languages: Dict, repo_dir: Path) -> None:
    """Generate language analysis documentation."""
    if not languages:
        return
    
    output_file = repo_dir / "LANGUAGES.md"
    
    total_bytes = sum(languages.values())
    
    with open(output_file, 'w') as f:
        f.write("# Language Analysis\n\n")
        f.write("## Language Distribution\n\n")
        
        for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (bytes_count / total_bytes) * 100
            bar_length = int(percentage / 2)
            bar = "█" * bar_length
            f.write(f"### {lang}\n\n")
            f.write(f"- **Bytes:** {bytes_count:,}\n")
            f.write(f"- **Percentage:** {percentage:.2f}%\n")
            f.write(f"- **Visual:** {bar}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Languages:** {len(languages)}\n")
        f.write(f"- **Total Bytes:** {total_bytes:,}\n")
        f.write(f"- **Primary Language:** {max(languages.items(), key=lambda x: x[1])[0]}\n")


def generate_mermaid_diagram(repo: Dict, tree_data: Dict, repo_dir: Path) -> None:
    """Generate Mermaid diagram for repository structure."""
    output_file = repo_dir / "ARCHITECTURE.md"
    
    with open(output_file, 'w') as f:
        f.write("# Architecture Diagram\n\n")
        f.write("## Repository Structure\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")
        f.write(f"    ROOT[{repo['name']}]\n")
        
        if tree_data and 'tree' in tree_data:
            # Get top-level directories
            top_dirs = set()
            for item in tree_data['tree']:
                if item['type'] == 'tree':
                    parts = item['path'].split('/')
                    if len(parts) > 0:
                        top_dirs.add(parts[0])
            
            # Create nodes for top directories
            for i, dir_name in enumerate(sorted(top_dirs)[:10]):  # Limit to 10 for clarity
                node_id = f"DIR{i}"
                f.write(f"    {node_id}[{dir_name}]\n")
                f.write(f"    ROOT --> {node_id}\n")
        
        f.write("```\n\n")
        
        # Component diagram
        f.write("## Component Overview\n\n")
        f.write("```mermaid\n")
        f.write("graph LR\n")
        f.write(f"    A[Repository: {repo['name']}]\n")
        
        if repo.get('language'):
            f.write(f"    B[Language: {repo['language']}]\n")
            f.write("    A --> B\n")
        
        f.write(f"    C[Stars: {repo['stargazers_count']}]\n")
        f.write(f"    D[Forks: {repo['forks_count']}]\n")
        f.write("    A --> C\n")
        f.write("    A --> D\n")
        
        f.write("```\n\n")


def generate_readme_summary(readme_content: str, repo_dir: Path) -> None:
    """Generate a summary of the README file."""
    if not readme_content:
        return
    
    output_file = repo_dir / "README_SUMMARY.md"
    
    with open(output_file, 'w') as f:
        f.write("# README Summary\n\n")
        f.write("## Original README Content\n\n")
        
        # Include first 50 lines of README
        lines = readme_content.split('\n')[:50]
        for line in lines:
            f.write(f"{line}\n")
        
        if len(readme_content.split('\n')) > 50:
            f.write("\n*... (truncated for summary)*\n")


def generate_index(repos: List[Dict], output_dir: Path) -> None:
    """Generate master index of all documentation."""
    output_file = output_dir / "INDEX.md"
    
    with open(output_file, 'w') as f:
        f.write("# GitHub Repository Documentation Index\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n")
        f.write(f"**Total Repositories:** {len(repos)}\n\n")
        
        f.write("## Repositories\n\n")
        
        # Sort by stars
        sorted_repos = sorted(repos, key=lambda x: x['stargazers_count'], reverse=True)
        
        for repo in sorted_repos:
            f.write(f"### [{repo['name']}](./{repo['name']}/OVERVIEW.md)\n\n")
            
            if repo.get('description'):
                f.write(f"{repo['description']}\n\n")
            
            f.write(f"- ⭐ {repo['stargazers_count']} stars\n")
            f.write(f"- 🍴 {repo['forks_count']} forks\n")
            
            if repo.get('language'):
                f.write(f"- 📝 {repo['language']}\n")
            
            f.write(f"- 🔗 [{repo['html_url']}]({repo['html_url']})\n")
            
            # Link to generated docs
            repo_docs_dir = output_dir / repo['name']
            if repo_docs_dir.exists():
                f.write(f"\n**Documentation:**\n")
                if (repo_docs_dir / "OVERVIEW.md").exists():
                    f.write(f"- [Overview](./{repo['name']}/OVERVIEW.md)\n")
                if (repo_docs_dir / "FILE_STRUCTURE.md").exists():
                    f.write(f"- [File Structure](./{repo['name']}/FILE_STRUCTURE.md)\n")
                if (repo_docs_dir / "LANGUAGES.md").exists():
                    f.write(f"- [Languages](./{repo['name']}/LANGUAGES.md)\n")
                if (repo_docs_dir / "ARCHITECTURE.md").exists():
                    f.write(f"- [Architecture](./{repo['name']}/ARCHITECTURE.md)\n")
            
            f.write("\n---\n\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive documentation for GitHub repositories"
    )
    parser.add_argument(
        "username",
        help="GitHub username (use 'me' for authenticated user)"
    )
    parser.add_argument(
        "--output-dir",
        default="./github_docs",
        help="Output directory for documentation"
    )
    parser.add_argument(
        "--include-diagrams",
        action="store_true",
        help="Generate architecture diagrams"
    )
    parser.add_argument(
        "--include-file-structure",
        action="store_true",
        default=True,
        help="Include file structure documentation"
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        help="Maximum number of repositories to document"
    )
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = GitHubOperationsTool()
    
    # Determine username
    username = None if args.username.lower() == "me" else args.username
    
    print(f"Generating documentation for: {username or 'authenticated user'}")
    print(f"This may take a while...\n")
    
    # Get repositories
    result = tool.list_user_repos(username=username, max_repos=args.max_repos)
    
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1
    
    repos = result["data"]
    print(f"Found {len(repos)} repositories\n")
    
    # Create output directory
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each repository
    for i, repo in enumerate(repos, 1):
        repo_name = repo['name']
        print(f"[{i}/{len(repos)}] Documenting {repo_name}...")
        
        # Create repository directory
        repo_dir = output_dir / repo_name
        repo_dir.mkdir(exist_ok=True)
        
        # Generate overview
        generate_repository_overview(repo, repo_dir)
        
        # Get and document languages
        owner = repo['owner']['login']
        lang_result = tool.list_repo_languages(owner, repo_name)
        if lang_result["success"]:
            generate_language_analysis_doc(lang_result["data"], repo_dir)
        
        # Get and document file structure
        if args.include_file_structure:
            tree_result = tool.get_repo_tree(owner, repo_name)
            if tree_result["success"]:
                generate_file_structure_doc(tree_result["data"], repo_dir)
                
                # Generate diagrams
                if args.include_diagrams:
                    generate_mermaid_diagram(repo, tree_result["data"], repo_dir)
        
        # Get README
        readme_result = tool.get_repo_readme(owner, repo_name)
        if readme_result["success"]:
            generate_readme_summary(readme_result["data"]["content"], repo_dir)
    
    # Generate master index
    print("\nGenerating master index...")
    generate_index(repos, output_dir)
    
    print(f"\n✅ Documentation generation complete!")
    print(f"   Total repositories documented: {len(repos)}")
    print(f"   Documentation location: {output_dir}")
    print(f"   Index file: {output_dir / 'INDEX.md'}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
