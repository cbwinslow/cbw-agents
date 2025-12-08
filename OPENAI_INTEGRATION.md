# OpenAI Integration Guide

Complete guide for integrating CBW Agents tools with OpenAI and other AI frameworks.

## 📚 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Tool Categories](#tool-categories)
- [Integration Examples](#integration-examples)
- [Agent Configurations](#agent-configurations)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

CBW Agents provides a comprehensive collection of OpenAI-compatible tools and agent configurations. All tools are designed with:

- **OpenAI Function Calling Support**: Native integration with OpenAI's function calling API
- **Portable Design**: Can be used anywhere, no dependencies on specific infrastructure
- **Modular Architecture**: Mix and match tools based on your needs
- **Range of Complexity**: From simple web browsing to complex system diagnostics

### Tool Complexity Levels

- **Simple**: Single-purpose tools with straightforward operations (web browsing, file downloading)
- **Medium**: Tools with state management and data persistence (bookmarks, price tracking)
- **Complex**: Advanced tools with multiple sub-operations (web crawling, system monitoring)

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies
pip install requests beautifulsoup4 lxml html2text Pillow psutil

# Optional dependencies for specific tools
pip install openai langchain crewai
```

### 2. Import and Use a Tool

```python
from tools.web_browsing import WebBrowsingTool

# Initialize tool
browser = WebBrowsingTool()

# Use the tool
result = browser.browse_url("https://example.com")
print(result)
```

### 3. Use with OpenAI Function Calling

```python
import openai
from tools.web_browsing import OPENAI_FUNCTIONS, WebBrowsingTool

# Initialize OpenAI client
client = openai.OpenAI(api_key="your-api-key")

# Create tool instance
browser = WebBrowsingTool()

# Define function handler
def handle_function_call(function_name, arguments):
    if function_name == "browse_url":
        return browser.browse_url(**arguments)
    # Add other functions...

# Use in chat completion
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "user", "content": "Browse https://example.com and tell me what you find"}
    ],
    tools=OPENAI_FUNCTIONS,
    tool_choice="auto"
)

# Handle function calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        result = handle_function_call(function_name, arguments)
```

## Tool Categories

### 🌐 Web Operations

#### Web Browsing Tool
**Module**: `tools.web_browsing`
**Complexity**: Simple

**Capabilities**:
- Browse URLs and extract content
- Navigate through links
- Search page content
- Analyze page structure

**Example**:
```python
from tools.web_browsing import WebBrowsingTool

browser = WebBrowsingTool()

# Browse a URL
result = browser.browse_url("https://example.com", extract_content=True)
print(f"Title: {result['title']}")
print(f"Main content: {result['main_content'][:200]}...")

# Search within page
search_result = browser.search_page("keyword")
print(f"Found {search_result['occurrences']} matches")
```

#### Web to Markdown Tool
**Module**: `tools.web_to_markdown`
**Complexity**: Simple

**Capabilities**:
- Convert web pages to Markdown
- Preserve links and images
- Extract metadata
- Batch conversion

**Example**:
```python
from tools.web_to_markdown import WebToMarkdownTool

converter = WebToMarkdownTool()

# Convert URL to Markdown
result = converter.convert_url("https://example.com")
print(result['markdown'])

# Save to file
converter.convert_to_file("https://example.com", "output.md")
```

#### Web Crawler Tool
**Module**: `tools.web_crawler`
**Complexity**: Complex

**Capabilities**:
- Systematic site crawling
- Link discovery and mapping
- Broken link detection
- Email extraction

**Example**:
```python
from tools.web_crawler import WebCrawlerTool

crawler = WebCrawlerTool()

# Crawl a site
result = crawler.crawl_site(
    "https://example.com",
    max_depth=2,
    same_domain_only=True
)
print(f"Crawled {result['pages_crawled']} pages")

# Find broken links
broken_links = crawler.find_broken_links("https://example.com")
print(f"Found {broken_links['broken_links_count']} broken links")
```

### 📥 File Operations

#### File Downloader Tool
**Module**: `tools.file_downloader`
**Complexity**: Simple

**Capabilities**:
- Download files from URLs
- Progress tracking
- Integrity verification (SHA256)
- Batch downloads

**Example**:
```python
from tools.file_downloader import FileDownloaderTool

downloader = FileDownloaderTool(download_dir="./downloads")

# Download a file
result = downloader.download_file("https://example.com/file.pdf")
print(f"Downloaded to: {result['file_path']}")
print(f"Size: {result['size_mb']} MB")

# Get file info without downloading
info = downloader.get_file_info("https://example.com/file.pdf")
print(f"File size: {info['size_mb']} MB")
```

### 💾 Data Collection

#### Bookmarks Manager Tool
**Module**: `tools.bookmarks_manager`
**Complexity**: Medium

**Capabilities**:
- Add and organize bookmarks
- Tag-based organization
- Full-text search
- Export functionality

**Example**:
```python
from tools.bookmarks_manager import BookmarksManagerTool

bookmarks = BookmarksManagerTool()

# Add a bookmark
bookmarks.add_bookmark(
    url="https://example.com",
    title="Example Site",
    tags=["development", "tutorial"],
    folder="Learning"
)

# Search bookmarks
results = bookmarks.search_bookmarks(
    query="development",
    tags=["tutorial"]
)
print(f"Found {results['count']} bookmarks")
```

#### Price Data Collector Tool
**Module**: `tools.price_data_collector`
**Complexity**: Medium

**Capabilities**:
- Collect price data from sources
- Historical tracking
- Price alerts
- Trend analysis

**Example**:
```python
from tools.price_data_collector import PriceDataCollectorTool

collector = PriceDataCollectorTool()

# Collect price
result = collector.collect_price(
    source="amazon",
    item_id="product-123",
    url="https://example.com/product",
    selector=".price"
)

# Get price history
history = collector.get_price_history("product-123", days=30)
print(f"Average price: ${history['statistics']['average_price']}")
print(f"Price volatility: {history['statistics']['volatility']}%")
```

### 🖼️ Analysis Tools

#### Image Analyzer Tool
**Module**: `tools.image_analyzer`
**Complexity**: Medium

**Capabilities**:
- Image properties analysis
- EXIF metadata extraction
- Dominant color detection
- Image comparison

**Example**:
```python
from tools.image_analyzer import ImageAnalyzerTool

analyzer = ImageAnalyzerTool()

# Analyze an image
result = analyzer.analyze_image(
    "https://example.com/image.jpg",
    include_metadata=True,
    include_colors=True
)

print(f"Size: {result['properties']['width']}x{result['properties']['height']}")
print(f"Dominant colors: {result['colors']['dominant_colors']}")
```

### 🖥️ Infrastructure Tools

#### Network Monitor Tool
**Module**: `tools.network_monitor`
**Complexity**: Complex

**Capabilities**:
- Ping hosts for connectivity
- Port scanning
- DNS lookups
- Connection testing

**Example**:
```python
from tools.network_monitor import NetworkMonitorTool

monitor = NetworkMonitorTool()

# Ping a host
ping_result = monitor.ping_host("google.com", count=4)
print(f"Avg latency: {ping_result['statistics']['avg_ms']} ms")

# Check if port is open
port_result = monitor.check_port("example.com", 443)
print(f"Port 443: {port_result['status']}")

# Comprehensive connection test
test = monitor.test_connection("example.com", 443, "https")
print(f"Overall status: {test['overall_status']}")
```

#### System Diagnostics Tool
**Module**: `tools.system_diagnostics`
**Complexity**: Complex

**Capabilities**:
- CPU monitoring
- Memory analysis
- Disk usage tracking
- Process monitoring
- Comprehensive health checks

**Example**:
```python
from tools.system_diagnostics import SystemDiagnosticsTool

diagnostics = SystemDiagnosticsTool()

# Check system health
health = diagnostics.health_check()
print(f"Health status: {health['health_status']}")
if health['issues']:
    print(f"Issues: {health['issues']}")

# Check CPU
cpu = diagnostics.check_cpu()
print(f"CPU usage: {cpu['cpu_percent_total']}%")

# Check memory
memory = diagnostics.check_memory()
print(f"Memory: {memory['virtual_memory']['percent_used']}% used")
```

## Integration Examples

### OpenAI Function Calling

```python
import openai
import json
from tools.web_browsing import OPENAI_FUNCTIONS, WebBrowsingTool
from tools.file_downloader import OPENAI_FUNCTIONS as DOWNLOAD_FUNCTIONS, FileDownloaderTool

# Initialize tools
browser = WebBrowsingTool()
downloader = FileDownloaderTool()

# Combine function definitions
all_functions = OPENAI_FUNCTIONS + DOWNLOAD_FUNCTIONS

# Function router
def execute_function(name, args):
    if name == "browse_url":
        return browser.browse_url(**args)
    elif name == "download_file":
        return downloader.download_file(**args)
    # Add more functions...

# Use with OpenAI
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": "Browse example.com"}],
    tools=all_functions
)
```

### LangChain Integration

```python
from langchain.agents import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from tools.web_browsing import WebBrowsingTool

# Create tool instance
browser = WebBrowsingTool()

# Create LangChain tool
browse_tool = Tool(
    name="web_browser",
    func=lambda url: browser.browse_url(url),
    description="Browse a URL and extract its content"
)

# Initialize agent
llm = ChatOpenAI(model="gpt-4")
agent = initialize_agent(
    [browse_tool],
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Use agent
result = agent.run("Browse https://example.com and summarize it")
```

### CrewAI Integration

```python
from crewai import Agent, Task, Crew
from tools.web_crawler import WebCrawlerTool

# Create tool instance
crawler = WebCrawlerTool()

# Define agent with custom tool
researcher = Agent(
    role='Web Researcher',
    goal='Crawl websites and extract information',
    backstory='Expert in web scraping and data extraction',
    tools=[crawler],
    verbose=True
)

# Create task
task = Task(
    description='Crawl example.com and create a site map',
    agent=researcher
)

# Execute
crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
```

## Agent Configurations

Pre-configured agents for common use cases:

### Web Browsing Agent
**Config**: `agents/web_browsing_agent.json`
**Tools**: web_browsing
**Use Case**: General web navigation and content extraction

### Price Tracking Agent
**Config**: `agents/price_tracking_agent.json`
**Tools**: price_data_collector, web_browsing
**Use Case**: E-commerce price monitoring and alerts

### Web Crawler Agent
**Config**: `agents/web_crawler_agent.json`
**Tools**: web_crawler, web_browsing
**Use Case**: Site mapping and content discovery

### Network Admin Agent
**Config**: `agents/network_admin_agent.json`
**Tools**: network_monitor, system_diagnostics
**Use Case**: Network monitoring and diagnostics

### System Admin Agent
**Config**: `agents/sysadmin_agent.json`
**Tools**: system_diagnostics, network_monitor
**Use Case**: System health monitoring

## Best Practices

### 1. Error Handling

All tools return consistent response format:
```python
{
    "success": True/False,
    "data": {...},        # On success
    "error": "message"   # On failure
}
```

Always check the `success` field:
```python
result = tool.some_function()
if result["success"]:
    # Process data
    data = result["data"]
else:
    # Handle error
    print(f"Error: {result['error']}")
```

### 2. Rate Limiting

For web-based tools, respect rate limits:
```python
# Built-in rate limiting
browser = WebBrowsingTool(delay_between_requests=1.5)
```

### 3. Resource Management

Use context managers or cleanup:
```python
from tools.bookmarks_manager import BookmarksManagerTool

bookmarks = BookmarksManagerTool()
try:
    # Use bookmarks
    pass
finally:
    # Cleanup happens automatically in __del__
    del bookmarks
```

### 4. Security

- Always validate URLs before browsing
- Use SSL verification for downloads
- Don't expose sensitive data in logs
- Follow robots.txt for web crawling

### 5. Performance

- Use batch operations when available
- Cache results when appropriate
- Set appropriate timeouts
- Monitor resource usage for complex operations

## Troubleshooting

### Import Errors

```python
# Make sure you're in the correct directory
import sys
sys.path.append('/path/to/cbw-agents')

from tools.web_browsing import WebBrowsingTool
```

### SSL Certificate Errors

```python
# For development only - disable SSL verification
downloader = FileDownloaderTool()
result = downloader.download_file(url, verify_ssl=False)
```

### Timeout Issues

```python
# Increase timeout for slow connections
browser = WebBrowsingTool(timeout=60)
```

### Memory Issues

```python
# For large crawls, limit pages
crawler = WebCrawlerTool(max_pages=50)
```

## Advanced Usage

### Custom Tool Integration

Create your own OpenAI-compatible tool:

```python
class CustomTool:
    def my_function(self, param: str) -> Dict[str, Any]:
        try:
            # Your logic here
            return {
                "success": True,
                "result": "data"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Define OpenAI function
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "my_function",
            "description": "Description of what it does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param"]
            }
        }
    }
]
```

## Support

- **Documentation**: See individual tool files for detailed API docs
- **Examples**: Check `examples/` directory for more use cases
- **Issues**: Report issues on the GitHub repository
- **Tool Registry**: See `openai_tools/tool_registry.json` for complete tool catalog

## License

See main repository LICENSE file for terms.

---

**Last Updated**: 2025-12-08
**Version**: 1.0.0
