# Quick Start Guide

Get started with CBW Agents OpenAI-compatible tools in 5 minutes.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cbwinslow/cbw-agents.git
cd cbw-agents
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies**:
- requests (web operations)
- beautifulsoup4 (HTML parsing)
- lxml (XML parsing)
- html2text (markdown conversion)
- Pillow (image processing)
- psutil (system monitoring)

## Your First Tool

### Example 1: Web Browsing

```python
from tools.web_browsing import WebBrowsingTool

# Initialize
browser = WebBrowsingTool()

# Browse a website
result = browser.browse_url("https://example.com")

if result["success"]:
    print(f"Title: {result['title']}")
    print(f"Content: {result['text_content'][:200]}...")
    print(f"Links found: {len(result['links'])}")
```

### Example 2: Download Files

```python
from tools.file_downloader import FileDownloaderTool

# Initialize
downloader = FileDownloaderTool(download_dir="./downloads")

# Download a file
result = downloader.download_file("https://example.com/file.pdf")

if result["success"]:
    print(f"Downloaded: {result['filename']}")
    print(f"Size: {result['size_mb']} MB")
```

### Example 3: Convert to Markdown

```python
from tools.web_to_markdown import WebToMarkdownTool

# Initialize
converter = WebToMarkdownTool()

# Convert webpage
result = converter.convert_url("https://example.com")

if result["success"]:
    print(result["markdown"])
```

## Using with OpenAI

### Basic Integration

```python
import openai
from tools.web_browsing import OPENAI_FUNCTIONS, WebBrowsingTool

# Initialize
client = openai.OpenAI(api_key="your-key")
browser = WebBrowsingTool()

# Define function handler
def execute_function(name, args):
    if name == "browse_url":
        return browser.browse_url(**args)
    # Add more functions...

# Use with OpenAI
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "user", "content": "Browse https://example.com"}
    ],
    tools=OPENAI_FUNCTIONS,
    tool_choice="auto"
)

# Handle function calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        result = execute_function(name, args)
```

## Tool Categories

### 🌐 Web Operations
- **web_browsing** - Navigate and extract content
- **file_downloader** - Download files with tracking
- **web_to_markdown** - Convert pages to markdown
- **web_crawler** - Crawl websites systematically

### 💾 Data Collection
- **bookmarks_manager** - Organize and search bookmarks
- **price_data_collector** - Track prices with history

### 🖼️ Analysis
- **image_analyzer** - Analyze images and metadata

### 🖥️ Infrastructure
- **network_monitor** - Network diagnostics
- **system_diagnostics** - System health monitoring

## Common Patterns

### Pattern 1: Error Handling

All tools return consistent format:

```python
result = tool.some_function()

if result["success"]:
    # Handle success
    data = result["data"]
else:
    # Handle error
    print(f"Error: {result['error']}")
```

### Pattern 2: Tool Chaining

```python
from tools.web_browsing import WebBrowsingTool
from tools.web_to_markdown import WebToMarkdownTool
from tools.bookmarks_manager import BookmarksManagerTool

# Chain tools together
browser = WebBrowsingTool()
converter = WebToMarkdownTool()
bookmarks = BookmarksManagerTool()

# Browse -> Convert -> Save
page = browser.browse_url("https://example.com")
markdown = converter.convert_url("https://example.com")
bookmarks.add_bookmark(
    url="https://example.com",
    title=page['title'],
    tags=["important"]
)
```

### Pattern 3: Batch Operations

```python
from tools.file_downloader import FileDownloaderTool

downloader = FileDownloaderTool()

# Download multiple files
urls = [
    "https://example.com/file1.pdf",
    "https://example.com/file2.pdf",
    "https://example.com/file3.pdf"
]

result = downloader.download_multiple(urls)
print(f"Downloaded: {result['successful']}/{result['total_files']}")
```

## Using Agent Configurations

### Load an Agent Configuration

```python
import json

# Load agent config
with open('agents/web_browsing_agent.json', 'r') as f:
    config = json.load(f)

print(f"Agent: {config['agent_name']}")
print(f"Tools: {config['tools']}")
print(f"Capabilities: {config['capabilities']}")
```

### Configure Tool Behavior

```python
from tools.web_crawler import WebCrawlerTool

# Configure based on agent settings
crawler = WebCrawlerTool(
    timeout=30,
    delay=1.0,
    max_pages=100
)

# Use with agent configuration
result = crawler.crawl_site(
    "https://example.com",
    max_depth=2,
    same_domain_only=True
)
```

## Running Examples

Try the included examples:

```bash
# Web browsing example
python examples/example_web_browsing.py

# OpenAI integration example
python examples/example_openai_integration.py

# Price tracking example
python examples/example_price_tracking.py
```

## Next Steps

### 1. Explore Tools
Read [TOOLS_CATALOG.md](TOOLS_CATALOG.md) for complete tool reference.

### 2. Integration Guide
See [OPENAI_INTEGRATION.md](OPENAI_INTEGRATION.md) for detailed integration examples.

### 3. Tool Registry
Check [openai_tools/tool_registry.json](openai_tools/tool_registry.json) for metadata.

### 4. Customize Agents
Modify agent configurations in `agents/` to fit your needs.

## Troubleshooting

### Import Errors

```python
# Make sure you're in the correct directory
import sys
sys.path.append('/path/to/cbw-agents')
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install requests beautifulsoup4 lxml html2text Pillow psutil
```

### SSL Errors

```python
# For development only
result = tool.download_file(url, verify_ssl=False)
```

### Timeout Issues

```python
# Increase timeout for slow connections
tool = WebBrowsingTool(timeout=60)
```

## Best Practices

1. **Always check success**: `if result["success"]:`
2. **Handle errors gracefully**: Print or log `result["error"]`
3. **Use timeouts**: Set appropriate timeout values
4. **Respect rate limits**: Add delays between requests
5. **Validate inputs**: Check URLs and parameters
6. **Close resources**: Tools handle cleanup automatically

## Getting Help

- **Documentation**: See individual tool files for API docs
- **Examples**: Check `examples/` directory
- **Tool Catalog**: See [TOOLS_CATALOG.md](TOOLS_CATALOG.md)
- **Integration Guide**: See [OPENAI_INTEGRATION.md](OPENAI_INTEGRATION.md)

## License

See main repository LICENSE for terms.

---

**Last Updated**: 2025-12-08
**Version**: 1.0.0

Ready to build? Start with the examples and explore the tools! 🚀
