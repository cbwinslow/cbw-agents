#!/usr/bin/env python3
"""
GitHub Account Analyzer

Comprehensive analysis tool for GitHub accounts and all their repositories.
Generates detailed reports including:
- Repository statistics and trends
- Technology stack analysis
- Activity patterns
- Code quality metrics
- Recommendations

Usage:
    python scripts/github_analyze_account.py USERNAME
    python scripts/github_analyze_account.py USERNAME --deep-analysis
    python scripts/github_analyze_account.py USERNAME --output-dir ./analysis --generate-diagrams
"""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.github_operations import GitHubOperationsTool


def analyze_languages(repos: List[Dict]) -> Dict[str, Any]:
    """Analyze language usage across repositories."""
    language_count = Counter()
    total_repos = len(repos)
    repos_by_language = {}
    
    for repo in repos:
        lang = repo.get('language')
        if lang:
            language_count[lang] += 1
            if lang not in repos_by_language:
                repos_by_language[lang] = []
            repos_by_language[lang].append(repo['name'])
    
    return {
        "total_languages": len(language_count),
        "primary_languages": dict(language_count.most_common(10)),
        "language_distribution": {
            lang: {
                "count": count,
                "percentage": (count / total_repos) * 100,
                "repositories": repos_by_language[lang]
            }
            for lang, count in language_count.items()
        }
    }


def analyze_activity(repos: List[Dict]) -> Dict[str, Any]:
    """Analyze repository activity patterns."""
    from datetime import datetime as dt
    
    current_year = dt.now().year
    created_by_year = Counter()
    updated_by_year = Counter()
    
    active_repos = 0
    inactive_repos = 0
    archived_repos = 0
    
    for repo in repos:
        # Parse dates
        created = dt.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
        updated = dt.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
        
        created_by_year[created.year] += 1
        updated_by_year[updated.year] += 1
        
        # Activity status (updated in last 6 months)
        # Using approximate 30-day month calculation
        days_since_update = (dt.now().replace(tzinfo=created.tzinfo) - updated).days
        if days_since_update < 180:  # ~6 months
            active_repos += 1
        else:
            inactive_repos += 1
        
        if repo.get('archived', False):
            archived_repos += 1
    
    return {
        "active_repositories": active_repos,
        "inactive_repositories": inactive_repos,
        "archived_repositories": archived_repos,
        "creation_timeline": dict(created_by_year),
        "update_timeline": dict(updated_by_year),
        "activity_rate": (active_repos / len(repos)) * 100 if repos else 0
    }


def analyze_popularity(repos: List[Dict]) -> Dict[str, Any]:
    """Analyze repository popularity metrics."""
    total_stars = sum(r['stargazers_count'] for r in repos)
    total_forks = sum(r['forks_count'] for r in repos)
    total_watchers = sum(r['watchers_count'] for r in repos)
    
    # Top repositories
    top_by_stars = sorted(repos, key=lambda x: x['stargazers_count'], reverse=True)[:10]
    top_by_forks = sorted(repos, key=lambda x: x['forks_count'], reverse=True)[:10]
    
    return {
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_watchers": total_watchers,
        "average_stars": total_stars / len(repos) if repos else 0,
        "average_forks": total_forks / len(repos) if repos else 0,
        "top_starred": [
            {
                "name": r['name'],
                "stars": r['stargazers_count'],
                "forks": r['forks_count'],
                "url": r['url']
            }
            for r in top_by_stars[:5]
        ],
        "top_forked": [
            {
                "name": r['name'],
                "forks": r['forks_count'],
                "stars": r['stargazers_count'],
                "url": r['url']
            }
            for r in top_by_forks[:5]
        ]
    }


def analyze_repository_characteristics(repos: List[Dict]) -> Dict[str, Any]:
    """Analyze repository characteristics and patterns."""
    total_size = sum(r['size'] for r in repos)
    
    private_count = sum(1 for r in repos if r['private'])
    public_count = len(repos) - private_count
    
    forked_count = sum(1 for r in repos if r.get('fork', False))
    original_count = len(repos) - forked_count
    
    has_issues = sum(1 for r in repos if r.get('has_issues', False))
    has_wiki = sum(1 for r in repos if r.get('has_wiki', False))
    has_pages = sum(1 for r in repos if r.get('has_pages', False))
    
    # Topics analysis
    all_topics = []
    for repo in repos:
        all_topics.extend(repo.get('topics', []))
    
    topic_count = Counter(all_topics)
    
    return {
        "total_size_kb": total_size,
        "total_size_mb": total_size / 1024,
        "average_size_kb": total_size / len(repos) if repos else 0,
        "public_repositories": public_count,
        "private_repositories": private_count,
        "original_repositories": original_count,
        "forked_repositories": forked_count,
        "repositories_with_issues": has_issues,
        "repositories_with_wiki": has_wiki,
        "repositories_with_pages": has_pages,
        "total_topics": len(topic_count),
        "top_topics": dict(topic_count.most_common(15)),
        "visibility_ratio": {
            "public_percentage": (public_count / len(repos)) * 100 if repos else 0,
            "private_percentage": (private_count / len(repos)) * 100 if repos else 0
        }
    }


def generate_recommendations(analysis: Dict) -> List[str]:
    """Generate recommendations based on analysis."""
    recommendations = []
    
    # Activity recommendations
    if analysis['activity']['inactive_repositories'] > analysis['activity']['active_repositories']:
        recommendations.append(
            "⚠️ Many inactive repositories detected. Consider archiving or updating inactive projects."
        )
    
    # Documentation recommendations
    repos = analysis.get('repositories', [])
    no_description = sum(1 for r in repos if not r.get('description'))
    if no_description > len(repos) * 0.3:
        recommendations.append(
            f"📝 {no_description} repositories lack descriptions. Adding descriptions improves discoverability."
        )
    
    # Popularity recommendations
    avg_stars = analysis['popularity']['average_stars']
    if avg_stars < 1:
        recommendations.append(
            "⭐ Consider promoting your repositories to increase visibility and engagement."
        )
    
    # Language diversity
    if analysis['languages']['total_languages'] == 1:
        recommendations.append(
            "🔧 Portfolio shows expertise in a single language. Consider diversifying to demonstrate broader skills."
        )
    
    # Topics usage
    if analysis['characteristics']['total_topics'] < len(repos) * 0.5:
        recommendations.append(
            "🏷️ Many repositories lack topics. Add topics to improve searchability and organization."
        )
    
    # Features
    has_wiki = analysis['characteristics']['repositories_with_wiki']
    has_pages = analysis['characteristics']['repositories_with_pages']
    if has_wiki < len(repos) * 0.2:
        recommendations.append(
            "📚 Consider enabling wikis for projects that need detailed documentation."
        )
    if has_pages < 3 and len(repos) > 5:
        recommendations.append(
            "🌐 GitHub Pages can be used to host project documentation or portfolio websites."
        )
    
    return recommendations


def generate_markdown_report(analysis: Dict, output_file: Path) -> None:
    """Generate comprehensive markdown report."""
    with open(output_file, 'w') as f:
        f.write("# GitHub Account Analysis Report\n\n")
        f.write(f"**Account:** {analysis['username']}\n")
        f.write(f"**Analysis Date:** {analysis['analyzed_at']}\n")
        f.write(f"**Total Repositories:** {analysis['total_repositories']}\n\n")
        
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        pop = analysis['popularity']
        f.write(f"- **Total Stars:** ⭐ {pop['total_stars']:,}\n")
        f.write(f"- **Total Forks:** 🍴 {pop['total_forks']:,}\n")
        f.write(f"- **Primary Languages:** {len(analysis['languages']['primary_languages'])}\n")
        f.write(f"- **Active Repositories:** {analysis['activity']['active_repositories']}\n")
        f.write(f"- **Repository Size:** {analysis['characteristics']['total_size_mb']:.2f} MB\n\n")
        
        # Language Analysis
        f.write("## Language Analysis\n\n")
        f.write(f"Total languages used: **{analysis['languages']['total_languages']}**\n\n")
        f.write("### Top Languages\n\n")
        for lang, data in sorted(
            analysis['languages']['language_distribution'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]:
            f.write(f"- **{lang}**: {data['count']} repositories ({data['percentage']:.1f}%)\n")
        f.write("\n")
        
        # Activity Analysis
        f.write("## Activity Analysis\n\n")
        act = analysis['activity']
        f.write(f"- **Active Repositories:** {act['active_repositories']} ({act['activity_rate']:.1f}%)\n")
        f.write(f"- **Inactive Repositories:** {act['inactive_repositories']}\n")
        f.write(f"- **Archived Repositories:** {act['archived_repositories']}\n\n")
        
        f.write("### Creation Timeline\n\n")
        for year in sorted(act['creation_timeline'].keys(), reverse=True)[:5]:
            f.write(f"- **{year}:** {act['creation_timeline'][year]} repositories created\n")
        f.write("\n")
        
        # Popularity Metrics
        f.write("## Popularity Metrics\n\n")
        f.write("### Top Starred Repositories\n\n")
        for repo in pop['top_starred']:
            f.write(f"- **[{repo['name']}]({repo['url']})**: ⭐ {repo['stars']:,} | 🍴 {repo['forks']:,}\n")
        f.write("\n")
        
        # Repository Characteristics
        f.write("## Repository Characteristics\n\n")
        char = analysis['characteristics']
        f.write(f"- **Public Repositories:** {char['public_repositories']}\n")
        f.write(f"- **Private Repositories:** {char['private_repositories']}\n")
        f.write(f"- **Original Repositories:** {char['original_repositories']}\n")
        f.write(f"- **Forked Repositories:** {char['forked_repositories']}\n")
        f.write(f"- **Average Repository Size:** {char['average_size_kb']:.2f} KB\n\n")
        
        if char['top_topics']:
            f.write("### Top Topics\n\n")
            for topic, count in list(char['top_topics'].items())[:10]:
                f.write(f"- **{topic}**: {count} repositories\n")
            f.write("\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        for rec in analysis['recommendations']:
            f.write(f"{rec}\n\n")
        
        f.write("---\n\n")
        f.write("*Report generated by CBW GitHub Analysis Tools*\n")


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive analysis of GitHub account and repositories"
    )
    parser.add_argument(
        "username",
        help="GitHub username (use 'me' for authenticated user)"
    )
    parser.add_argument(
        "--output-dir",
        default="./github_analysis",
        help="Output directory for analysis reports"
    )
    parser.add_argument(
        "--deep-analysis",
        action="store_true",
        help="Perform deep analysis including individual repository analysis (slower)"
    )
    parser.add_argument(
        "--format",
        nargs="+",
        choices=["json", "markdown", "all"],
        default=["json", "markdown"],
        help="Output format(s) for the analysis"
    )
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = GitHubOperationsTool()
    
    # Determine username
    username = None if args.username.lower() == "me" else args.username
    
    print(f"Analyzing GitHub account: {username or 'authenticated user'}")
    print(f"This may take a while...\n")
    
    # Get repositories
    result = tool.list_user_repos(username=username)
    
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1
    
    repos = result["data"]
    print(f"Found {len(repos)} repositories")
    
    # Perform analysis
    print("Analyzing languages...")
    language_analysis = analyze_languages(repos)
    
    print("Analyzing activity patterns...")
    activity_analysis = analyze_activity(repos)
    
    print("Analyzing popularity metrics...")
    popularity_analysis = analyze_popularity(repos)
    
    print("Analyzing repository characteristics...")
    characteristics_analysis = analyze_repository_characteristics(repos)
    
    # Compile full analysis
    analysis = {
        "username": username or "authenticated_user",
        "analyzed_at": datetime.now().isoformat(),
        "total_repositories": len(repos),
        "languages": language_analysis,
        "activity": activity_analysis,
        "popularity": popularity_analysis,
        "characteristics": characteristics_analysis,
        "repositories": repos
    }
    
    print("Generating recommendations...")
    analysis["recommendations"] = generate_recommendations(analysis)
    
    # Create output directory
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine formats
    formats = args.format
    if "all" in formats:
        formats = ["json", "markdown"]
    
    # Generate outputs
    username_str = username or "authenticated_user"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for fmt in formats:
        if fmt == "json":
            output_file = output_dir / f"{username_str}_analysis_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"✓ Generated JSON analysis: {output_file}")
        
        elif fmt == "markdown":
            output_file = output_dir / f"{username_str}_analysis_{timestamp}.md"
            generate_markdown_report(analysis, output_file)
            print(f"✓ Generated Markdown report: {output_file}")
    
    # Print summary
    print(f"\n📊 Analysis Summary:")
    print(f"   Total repositories: {analysis['total_repositories']}")
    print(f"   Primary languages: {len(language_analysis['primary_languages'])}")
    print(f"   Total stars: {popularity_analysis['total_stars']:,}")
    print(f"   Active repos: {activity_analysis['active_repositories']}")
    print(f"   Recommendations: {len(analysis['recommendations'])}")
    print(f"\n   Reports saved to: {output_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
