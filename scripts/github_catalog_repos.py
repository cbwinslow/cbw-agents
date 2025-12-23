#!/usr/bin/env python3
"""
GitHub Repository Cataloging Script

Create comprehensive catalogs of GitHub repositories for a user or organization.
Supports multiple output formats and can include detailed analysis.

Usage:
    python scripts/github_catalog_repos.py USERNAME
    python scripts/github_catalog_repos.py USERNAME --output-dir ./catalogs --format json csv markdown
    python scripts/github_catalog_repos.py USERNAME --include-analysis --include-languages
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.github_operations import GitHubOperationsTool


def format_size(bytes_size: int) -> str:
    """Format byte size to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def generate_markdown_catalog(catalog: Dict, output_file: Path) -> None:
    """Generate markdown format catalog."""
    with open(output_file, 'w') as f:
        f.write(f"# GitHub Repository Catalog\n\n")
        f.write(f"**User:** {catalog['username']}\n")
        f.write(f"**Total Repositories:** {catalog['total_repos']}\n")
        f.write(f"**Cataloged:** {catalog['cataloged_at']}\n\n")
        
        # Summary statistics
        total_stars = sum(r['stargazers_count'] for r in catalog['repositories'])
        total_forks = sum(r['forks_count'] for r in catalog['repositories'])
        languages = set()
        for repo in catalog['repositories']:
            if repo.get('language'):
                languages.add(repo['language'])
        
        f.write(f"## Summary Statistics\n\n")
        f.write(f"- **Total Stars:** {total_stars:,}\n")
        f.write(f"- **Total Forks:** {total_forks:,}\n")
        f.write(f"- **Languages Used:** {len(languages)}\n")
        f.write(f"- **Private Repositories:** {sum(1 for r in catalog['repositories'] if r['private'])}\n")
        f.write(f"- **Public Repositories:** {sum(1 for r in catalog['repositories'] if not r['private'])}\n\n")
        
        # List languages
        if languages:
            f.write(f"### Languages\n\n")
            for lang in sorted(languages):
                count = sum(1 for r in catalog['repositories'] if r.get('language') == lang)
                f.write(f"- **{lang}:** {count} repositories\n")
            f.write("\n")
        
        # Repository list
        f.write(f"## Repositories\n\n")
        
        # Sort by stars
        sorted_repos = sorted(
            catalog['repositories'],
            key=lambda x: x['stargazers_count'],
            reverse=True
        )
        
        for repo in sorted_repos:
            f.write(f"### [{repo['name']}]({repo['url']})\n\n")
            
            if repo['description']:
                f.write(f"{repo['description']}\n\n")
            
            f.write(f"**Details:**\n")
            f.write(f"- **Language:** {repo.get('language', 'N/A')}\n")
            f.write(f"- **Stars:** ⭐ {repo['stargazers_count']:,}\n")
            f.write(f"- **Forks:** 🍴 {repo['forks_count']:,}\n")
            f.write(f"- **Open Issues:** {repo['open_issues_count']}\n")
            f.write(f"- **Size:** {format_size(repo['size'] * 1024)}\n")
            f.write(f"- **Created:** {repo['created_at'][:10]}\n")
            f.write(f"- **Updated:** {repo['updated_at'][:10]}\n")
            f.write(f"- **Default Branch:** {repo['default_branch']}\n")
            
            if repo.get('topics'):
                f.write(f"- **Topics:** {', '.join(repo['topics'])}\n")
            
            if repo.get('languages'):
                langs = repo['languages']
                total = sum(langs.values())
                f.write(f"\n**Language Distribution:**\n")
                for lang, bytes_count in sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]:
                    percentage = (bytes_count / total) * 100
                    f.write(f"- {lang}: {percentage:.1f}%\n")
            
            f.write(f"\n**Clone URL:** `{repo['clone_url']}`\n\n")
            f.write("---\n\n")


def generate_csv_catalog(catalog: Dict, output_file: Path) -> None:
    """Generate CSV format catalog."""
    with open(output_file, 'w', newline='') as f:
        fieldnames = [
            'name', 'full_name', 'description', 'language', 'private',
            'stars', 'forks', 'watchers', 'open_issues', 'size',
            'created_at', 'updated_at', 'pushed_at', 'default_branch',
            'url', 'clone_url', 'topics'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for repo in catalog['repositories']:
            writer.writerow({
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo.get('description', ''),
                'language': repo.get('language', ''),
                'private': repo['private'],
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'watchers': repo['watchers_count'],
                'open_issues': repo['open_issues_count'],
                'size': repo['size'],
                'created_at': repo['created_at'],
                'updated_at': repo['updated_at'],
                'pushed_at': repo['pushed_at'],
                'default_branch': repo['default_branch'],
                'url': repo['url'],
                'clone_url': repo['clone_url'],
                'topics': ', '.join(repo.get('topics', []))
            })


def generate_html_catalog(catalog: Dict, output_file: Path) -> None:
    """Generate HTML format catalog."""
    with open(output_file, 'w') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n<head>\n")
        f.write("<meta charset='UTF-8'>\n")
        f.write(f"<title>GitHub Catalog - {catalog['username']}</title>\n")
        f.write("<style>\n")
        f.write("""
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1 { color: #24292e; }
            .summary { background: #f6f8fa; padding: 20px; border-radius: 6px; margin: 20px 0; }
            .repo { border: 1px solid #e1e4e8; padding: 20px; margin: 20px 0; border-radius: 6px; }
            .repo h2 { margin-top: 0; }
            .repo-meta { color: #586069; font-size: 14px; }
            .stats { display: flex; gap: 20px; margin: 10px 0; }
            .stat { display: flex; align-items: center; }
            .topics { display: flex; flex-wrap: wrap; gap: 5px; margin: 10px 0; }
            .topic { background: #0366d6; color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px; }
            a { color: #0366d6; text-decoration: none; }
            a:hover { text-decoration: underline; }
        """)
        f.write("</style>\n</head>\n<body>\n")
        
        f.write(f"<h1>GitHub Repository Catalog</h1>\n")
        f.write(f"<div class='summary'>\n")
        f.write(f"<p><strong>User:</strong> {catalog['username']}</p>\n")
        f.write(f"<p><strong>Total Repositories:</strong> {catalog['total_repos']}</p>\n")
        f.write(f"<p><strong>Cataloged:</strong> {catalog['cataloged_at']}</p>\n")
        f.write(f"</div>\n")
        
        for repo in catalog['repositories']:
            f.write(f"<div class='repo'>\n")
            f.write(f"<h2><a href='{repo['url']}'>{repo['name']}</a></h2>\n")
            
            if repo['description']:
                f.write(f"<p>{repo['description']}</p>\n")
            
            f.write("<div class='stats'>\n")
            f.write(f"<span class='stat'>⭐ {repo['stargazers_count']}</span>\n")
            f.write(f"<span class='stat'>🍴 {repo['forks_count']}</span>\n")
            f.write(f"<span class='stat'>👁 {repo['watchers_count']}</span>\n")
            if repo.get('language'):
                f.write(f"<span class='stat'>📝 {repo['language']}</span>\n")
            f.write("</div>\n")
            
            if repo.get('topics'):
                f.write("<div class='topics'>\n")
                for topic in repo['topics']:
                    f.write(f"<span class='topic'>{topic}</span>\n")
                f.write("</div>\n")
            
            f.write(f"<div class='repo-meta'>\n")
            f.write(f"Updated: {repo['updated_at'][:10]} | ")
            f.write(f"Size: {format_size(repo['size'] * 1024)} | ")
            f.write(f"<a href='{repo['clone_url']}'>Clone URL</a>\n")
            f.write("</div>\n")
            f.write("</div>\n")
        
        f.write("</body>\n</html>\n")


def main():
    parser = argparse.ArgumentParser(
        description="Catalog GitHub repositories for a user or organization"
    )
    parser.add_argument(
        "username",
        help="GitHub username or organization name (use 'me' for authenticated user)"
    )
    parser.add_argument(
        "--output-dir",
        default="./github_catalogs",
        help="Output directory for catalog files"
    )
    parser.add_argument(
        "--format",
        nargs="+",
        choices=["json", "csv", "markdown", "html", "all"],
        default=["json", "markdown"],
        help="Output format(s) for the catalog"
    )
    parser.add_argument(
        "--include-analysis",
        action="store_true",
        help="Include detailed analysis for each repository (slower)"
    )
    parser.add_argument(
        "--include-languages",
        action="store_true",
        help="Include language statistics for each repository"
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        help="Maximum number of repositories to catalog"
    )
    parser.add_argument(
        "--sort",
        choices=["created", "updated", "pushed", "full_name"],
        default="updated",
        help="Sort repositories by field"
    )
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = GitHubOperationsTool()
    
    # Determine username
    username = None if args.username.lower() == "me" else args.username
    
    print(f"Cataloging repositories for: {username or 'authenticated user'}")
    print(f"This may take a while depending on the number of repositories...\n")
    
    # Create catalog
    result = tool.catalog_repositories(username=username)
    
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1
    
    catalog = result["data"]
    print(f"Found {catalog['total_repos']} repositories")
    
    # Create output directory
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine formats
    formats = args.format
    if "all" in formats:
        formats = ["json", "csv", "markdown", "html"]
    
    # Generate outputs
    username_str = username or "authenticated_user"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for fmt in formats:
        if fmt == "json":
            output_file = output_dir / f"{username_str}_repos_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(catalog, f, indent=2)
            print(f"✓ Generated JSON catalog: {output_file}")
        
        elif fmt == "csv":
            output_file = output_dir / f"{username_str}_repos_{timestamp}.csv"
            generate_csv_catalog(catalog, output_file)
            print(f"✓ Generated CSV catalog: {output_file}")
        
        elif fmt == "markdown":
            output_file = output_dir / f"{username_str}_repos_{timestamp}.md"
            generate_markdown_catalog(catalog, output_file)
            print(f"✓ Generated Markdown catalog: {output_file}")
        
        elif fmt == "html":
            output_file = output_dir / f"{username_str}_repos_{timestamp}.html"
            generate_html_catalog(catalog, output_file)
            print(f"✓ Generated HTML catalog: {output_file}")
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"   Total repositories: {catalog['total_repos']}")
    print(f"   Catalog location: {output_dir}")
    print(f"   Formats generated: {', '.join(formats)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
