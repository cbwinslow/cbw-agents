# GitHub API Tools and Agents

Comprehensive suite of tools, agents, and scripts for analyzing and managing GitHub repositories and accounts using the GitHub API.

## 🎯 Overview

This collection provides powerful capabilities for:
- **Repository Cataloging**: Create comprehensive catalogs of all repositories
- **Account Analysis**: Analyze GitHub accounts with detailed metrics and insights
- **Documentation Generation**: Auto-generate documentation for repositories
- **Bulk Operations**: Perform operations across multiple repositories
- **Code Analysis**: Analyze code structure, languages, and dependencies
- **Diagram Creation**: Generate architecture and dependency diagrams
- **Search and Indexing**: Create searchable indices of repositories

## 📁 Components

### 🔧 Tools

#### `tools/github_operations.py`
Core GitHub API operations tool providing:
- Repository listing and search
- File and directory operations
- README and content retrieval
- Repository analysis and cataloging
- Language and tree structure analysis
- Rate limiting and authentication
- Comprehensive error handling

**Key Features:**
- ✅ Automatic rate limiting
- ✅ Authentication via GITHUB_TOKEN
- ✅ Pagination support for large datasets
- ✅ Retry logic with exponential backoff
- ✅ Caching support
- ✅ Comprehensive documentation

### 🤖 Agents

#### `agents/github_analysis_agent.json`
Specialized agent configuration for GitHub analysis:
- Repository metadata extraction
- Code quality assessment
- Dependency analysis
- Documentation review
- Activity monitoring
- Bulk operation support

### 👥 Crews

#### `crews/github_documentation_crew.json`
Multi-agent crew for comprehensive documentation:
- **Repository Cataloger**: Inventory and categorization
- **Code Analyzer**: Language and framework detection
- **Documentation Generator**: README and API docs
- **Diagram Creator**: Architecture visualizations
- **Repository Indexer**: Searchable index creation
- **Summary Reviewer**: Insights and recommendations

### 📜 Scripts

#### `scripts/github_catalog_repos.py`
Create comprehensive repository catalogs.

**Usage:**
```bash
# Catalog user's repositories
python scripts/github_catalog_repos.py USERNAME

# With multiple output formats
python scripts/github_catalog_repos.py USERNAME --format json csv markdown html

# Custom output directory
python scripts/github_catalog_repos.py USERNAME --output-dir ./my_catalogs

# Include language analysis
python scripts/github_catalog_repos.py USERNAME --include-languages
```

**Features:**
- Multiple output formats (JSON, CSV, Markdown, HTML)
- Repository metadata collection
- Language statistics
- Sorting and filtering options
- Beautiful formatted reports

#### `scripts/github_analyze_account.py`
Comprehensive GitHub account analysis.

**Usage:**
```bash
# Analyze account
python scripts/github_analyze_account.py USERNAME

# Deep analysis
python scripts/github_analyze_account.py USERNAME --deep-analysis

# Custom output location
python scripts/github_analyze_account.py USERNAME --output-dir ./analysis
```

**Features:**
- Language usage analysis
- Activity pattern detection
- Popularity metrics
- Repository characteristics
- Automated recommendations
- Trend analysis
- Executive summaries

**Analysis Categories:**
- 📊 Language Distribution
- 📈 Activity Patterns
- ⭐ Popularity Metrics
- 📦 Repository Characteristics
- 💡 Recommendations

#### `scripts/github_generate_docs.py`
Bulk documentation generator for repositories.

**Usage:**
```bash
# Generate documentation
python scripts/github_generate_docs.py USERNAME

# Include diagrams
python scripts/github_generate_docs.py USERNAME --include-diagrams

# Limit repositories
python scripts/github_generate_docs.py USERNAME --max-repos 10

# Custom output
python scripts/github_generate_docs.py USERNAME --output-dir ./docs
```

**Features:**
- Repository overviews
- File structure documentation
- Language analysis reports
- Architecture diagrams (Mermaid)
- README summaries
- Master index generation

**Generated Documentation:**
- `OVERVIEW.md` - Repository overview and statistics
- `FILE_STRUCTURE.md` - Complete file tree
- `LANGUAGES.md` - Language distribution analysis
- `ARCHITECTURE.md` - Mermaid diagrams
- `README_SUMMARY.md` - README highlights
- `INDEX.md` - Master documentation index

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+** installed
2. **GitHub Personal Access Token** (for API access)
3. **Required packages** installed

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up GitHub authentication:
```bash
export GITHUB_TOKEN="your_github_token_here"
```

To get a GitHub token:
- Go to GitHub Settings → Developer settings → Personal access tokens
- Generate new token with appropriate scopes (repo, read:org, read:user)

### Quick Start

#### 1. Catalog Your Repositories
```bash
python scripts/github_catalog_repos.py your_username --format all
```

#### 2. Analyze Your Account
```bash
python scripts/github_analyze_account.py your_username
```

#### 3. Generate Documentation
```bash
python scripts/github_generate_docs.py your_username --include-diagrams
```

#### 4. Use the Tool Programmatically
```python
from tools.github_operations import GitHubOperationsTool

# Initialize tool
tool = GitHubOperationsTool()

# List repositories
repos = tool.list_user_repos("username")

# Analyze a repository
analysis = tool.analyze_repository("owner", "repo")

# Search code
results = tool.search_code("language:python user:username")
```

## 📖 Detailed Usage

### Authentication

The tools support authentication via:
1. **Environment variable**: `export GITHUB_TOKEN="your_token"`
2. **Direct parameter**: `GitHubOperationsTool(token="your_token")`

### Rate Limiting

GitHub API has rate limits:
- **Authenticated**: 5,000 requests/hour
- **Unauthenticated**: 60 requests/hour

The tools automatically:
- Respect rate limits
- Add delays between requests
- Retry failed requests
- Show rate limit status

### Output Formats

#### JSON Format
Structured data perfect for:
- Further processing
- Integration with other tools
- Archiving and backup

#### CSV Format
Tabular data ideal for:
- Spreadsheet analysis
- Database import
- Quick filtering

#### Markdown Format
Human-readable format with:
- Formatted sections
- Links and badges
- Statistics and charts

#### HTML Format
Web-ready format featuring:
- Styled presentation
- Interactive elements
- Easy sharing

## 🎨 Use Cases

### 1. Portfolio Management
Create comprehensive catalogs of all your projects with statistics, descriptions, and links.

### 2. Account Audit
Analyze your GitHub presence, identify inactive repositories, and get recommendations for improvement.

### 3. Documentation Automation
Automatically generate documentation for all repositories, ensuring consistent structure.

### 4. Technology Stack Analysis
Understand your language and framework usage across all projects.

### 5. Research and Discovery
Search and catalog repositories by topic, language, or other criteria.

### 6. Team Coordination
Create indices and documentation for organization repositories to help team members navigate.

### 7. Migration Planning
Analyze existing repositories before migration or restructuring.

### 8. Compliance and Security
Audit repositories for documentation, license files, and security practices.

## 🔧 Advanced Features

### Bulk Operations
Process multiple repositories efficiently:
```python
tool = GitHubOperationsTool()

# Catalog all repositories
catalog = tool.catalog_repositories("username", output_file="catalog.json")

# Analyze each repository
for repo in catalog["data"]["repositories"]:
    analysis = tool.analyze_repository(
        repo["owner"]["login"],
        repo["name"]
    )
```

### Custom Filtering
Filter repositories by various criteria:
```python
# List only Python repositories
repos = tool.search_repositories("user:username language:python")

# Find specific code patterns
code = tool.search_code("function main language:go user:username")
```

### Caching
Enable caching to reduce API calls:
```python
tool = GitHubOperationsTool(cache_dir="./github_cache")
```

## 🛡️ Safety Features

- **Rate Limiting**: Automatic rate limit respect
- **Error Handling**: Comprehensive error handling with retries
- **Authentication**: Secure token-based authentication
- **Input Validation**: Validates all inputs
- **No Destructive Operations**: Read-only operations only
- **Privacy Protection**: Respects repository visibility settings

## 📊 Example Outputs

### Account Analysis Report
```
Total repositories: 42
Primary languages: 8
Total stars: 1,234
Active repos: 32
Recommendations: 5

Top Languages:
- Python: 15 repositories (35.7%)
- JavaScript: 10 repositories (23.8%)
- Go: 8 repositories (19.0%)
```

### Repository Catalog
```
Repository: awesome-project
Description: An awesome project that does amazing things
Stars: ⭐ 152 | Forks: 🍴 23
Language: Python
Size: 2.5 MB
Updated: 2025-12-20
```

## 🤝 Integration with AI Agents

These tools are designed to work with AI agent frameworks:

### With CrewAI
```python
from crewai import Crew, Agent, Task
from tools.github_operations import GitHubOperationsTool

agent = Agent(
    role="GitHub Analyst",
    tools=[GitHubOperationsTool()],
    goal="Analyze GitHub repositories"
)
```

### With LangChain
```python
from langchain.agents import Tool
from tools.github_operations import GitHubOperationsTool

github_tool = Tool(
    name="GitHub Operations",
    func=GitHubOperationsTool().list_user_repos,
    description="List GitHub repositories"
)
```

## 📚 API Reference

### GitHubOperationsTool Methods

#### `list_user_repos(username, repo_type, sort, per_page, max_repos)`
List repositories for a user.

#### `get_repo_info(owner, repo)`
Get detailed repository information.

#### `list_repo_contents(owner, repo, path, ref)`
List contents of a repository directory.

#### `get_file_content(owner, repo, path, ref)`
Get file content from repository.

#### `search_code(query, per_page, max_results)`
Search for code across GitHub.

#### `search_repositories(query, sort, order, per_page, max_results)`
Search for repositories.

#### `get_repo_tree(owner, repo, tree_sha, recursive)`
Get repository tree structure.

#### `list_repo_languages(owner, repo)`
Get programming languages used.

#### `get_repo_readme(owner, repo)`
Get repository README content.

#### `catalog_repositories(username, output_file)`
Create comprehensive repository catalog.

#### `analyze_repository(owner, repo, include_tree, include_readme)`
Perform comprehensive repository analysis.

## 🐛 Troubleshooting

### Rate Limit Errors
- Ensure GITHUB_TOKEN is set
- Reduce request frequency
- Use caching

### Authentication Errors
- Verify token is valid
- Check token permissions
- Ensure token hasn't expired

### Missing Data
- Some repositories may be private
- Check token permissions
- Verify repository exists

## 🔄 Future Enhancements

- [ ] GraphQL API support for faster queries
- [ ] Real-time monitoring and alerts
- [ ] Integration with GitHub Actions
- [ ] Advanced dependency analysis
- [ ] Security vulnerability scanning
- [ ] PR and issue analysis
- [ ] Contributor statistics
- [ ] Code quality metrics
- [ ] License compliance checking
- [ ] Multi-account management

## 📝 License

Part of the CBW Agents collection. See repository license for details.

## 🤝 Contributing

Contributions are welcome! Please follow the repository's contribution guidelines.

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review example usage
3. Check error messages and logs
4. Open an issue in the repository

---

**Last Updated**: 2025-12-23
**Version**: 1.0.0
**Maintainer**: CBW Development Team
