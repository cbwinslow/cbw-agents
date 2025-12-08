# Tools Catalog

Comprehensive catalog of all available OpenAI-compatible tools in CBW Agents.

## Overview

CBW Agents provides 9 modular, portable, OpenAI-compatible tools organized into 5 categories:

- **Web Operations** (4 tools): Browsing, crawling, conversion, downloading
- **Data Collection** (2 tools): Bookmarks, price tracking
- **Analysis** (1 tool): Image analysis
- **Infrastructure** (2 tools): Network and system monitoring
- **File Operations** (included in web operations): File management

## Quick Reference

| Tool | Complexity | Primary Use | Functions |
|------|-----------|-------------|-----------|
| web_browsing | Simple | Navigate & extract | 5 |
| file_downloader | Simple | Download files | 5 |
| web_to_markdown | Simple | Convert pages | 4 |
| bookmarks_manager | Medium | Organize links | 6 |
| image_analyzer | Medium | Analyze images | 4 |
| price_data_collector | Medium | Track prices | 4 |
| web_crawler | Complex | Crawl sites | 4 |
| network_monitor | Complex | Monitor network | 5 |
| system_diagnostics | Complex | Monitor system | 7 |

## Detailed Descriptions

### 🌐 Web Operations

#### 1. Web Browsing Tool
**File**: `tools/web_browsing.py`
**Complexity**: Simple
**OpenAI Compatible**: ✅

**Functions**:
- `browse_url(url, extract_content)` - Browse and extract page content
- `click_link(text)` - Navigate via link text
- `search_page(query)` - Search within current page
- `get_page_structure()` - Extract page structure
- `get_history()` - View browsing history

**Requirements**: requests, beautifulsoup4, lxml

**Use Cases**:
- Content extraction
- Web navigation
- Page analysis
- Research automation

---

#### 2. File Downloader Tool
**File**: `tools/file_downloader.py`
**Complexity**: Simple
**OpenAI Compatible**: ✅

**Functions**:
- `download_file(url, filename, verify_ssl)` - Download with tracking
- `download_multiple(urls)` - Batch downloads
- `get_file_info(url)` - Check without downloading
- `list_downloads()` - View downloaded files
- `delete_download(filename)` - Remove downloaded file

**Requirements**: requests, pathlib, hashlib

**Use Cases**:
- File downloading
- Content archiving
- Batch operations
- File management

---

#### 3. Web to Markdown Tool
**File**: `tools/web_to_markdown.py`
**Complexity**: Simple
**OpenAI Compatible**: ✅

**Functions**:
- `convert_url(url, include_metadata, include_links, include_images)` - Convert page to markdown
- `convert_html(html_content, base_url)` - Convert HTML string
- `convert_to_file(url, output_path)` - Save to file
- `batch_convert(urls)` - Convert multiple pages

**Requirements**: requests, beautifulsoup4, html2text

**Use Cases**:
- Documentation generation
- Content archiving
- Article conversion
- Research notes

---

#### 4. Web Crawler Tool
**File**: `tools/web_crawler.py`
**Complexity**: Complex
**OpenAI Compatible**: ✅

**Functions**:
- `crawl_site(start_url, max_depth, same_domain_only, respect_robots)` - Systematic crawling
- `crawl_sitemap(sitemap_url)` - Extract from sitemap
- `find_broken_links(url, check_depth)` - Detect broken links
- `extract_emails(url, max_depth)` - Find email addresses

**Requirements**: requests, beautifulsoup4, lxml, urllib.robotparser

**Use Cases**:
- Site mapping
- Content discovery
- SEO audits
- Data mining

---

### 💾 Data Collection

#### 5. Bookmarks Manager Tool
**File**: `tools/bookmarks_manager.py`
**Complexity**: Medium
**OpenAI Compatible**: ✅

**Functions**:
- `add_bookmark(url, title, description, tags, folder)` - Add new bookmark
- `search_bookmarks(query, tags, folder, favorite)` - Search and filter
- `update_bookmark(bookmark_id, **kwargs)` - Modify bookmark
- `delete_bookmark(bookmark_id)` - Remove bookmark
- `get_all_tags()` - List all tags
- `export_bookmarks(format)` - Export data

**Requirements**: sqlite3, pathlib, json

**Use Cases**:
- Research organization
- Link curation
- Content management
- Knowledge bases

---

#### 6. Price Data Collector Tool
**File**: `tools/price_data_collector.py`
**Complexity**: Medium
**OpenAI Compatible**: ✅

**Functions**:
- `collect_price(source, item_id, url, selector, api_key)` - Collect price data
- `collect_multiple(items)` - Batch collection
- `get_price_history(item_id, days)` - Historical data with stats
- `get_price_alerts(item_id, threshold_low, threshold_high)` - Alert checking

**Requirements**: requests, beautifulsoup4, sqlite3

**Use Cases**:
- Price tracking
- Market analysis
- Deal alerts
- Competitive intelligence

---

### 🖼️ Analysis

#### 7. Image Analyzer Tool
**File**: `tools/image_analyzer.py`
**Complexity**: Medium
**OpenAI Compatible**: ✅

**Functions**:
- `analyze_image(image_source, include_metadata, include_colors, include_histogram)` - Full analysis
- `compare_images(image1_source, image2_source)` - Compare two images
- `batch_analyze(image_sources)` - Analyze multiple images
- `get_thumbnail(image_source, max_size)` - Generate thumbnail

**Requirements**: Pillow, requests

**Use Cases**:
- Image analysis
- Metadata extraction
- Color analysis
- Image comparison

---

### 🖥️ Infrastructure

#### 8. Network Monitor Tool
**File**: `tools/network_monitor.py`
**Complexity**: Complex
**OpenAI Compatible**: ✅

**Functions**:
- `ping_host(host, count, timeout)` - Connectivity check
- `check_port(host, port, timeout)` - Port status
- `scan_ports(host, ports, common_only)` - Port scanning
- `dns_lookup(hostname)` - DNS resolution
- `test_connection(host, port, protocol)` - Comprehensive test

**Requirements**: socket, subprocess, platform, statistics

**Use Cases**:
- Network diagnostics
- Connectivity testing
- Port scanning
- DNS troubleshooting

---

#### 9. System Diagnostics Tool
**File**: `tools/system_diagnostics.py`
**Complexity**: Complex
**OpenAI Compatible**: ✅

**Functions**:
- `get_system_info()` - System information
- `check_cpu()` - CPU metrics
- `check_memory()` - Memory usage
- `check_disk(path)` - Disk usage
- `check_network()` - Network stats
- `check_processes(sort_by, limit)` - Process list
- `health_check()` - Comprehensive health check

**Requirements**: psutil, platform

**Use Cases**:
- System monitoring
- Performance analysis
- Health checks
- Resource tracking

---

## Integration Patterns

### Pattern 1: Single Tool Usage
```python
from tools.web_browsing import WebBrowsingTool

tool = WebBrowsingTool()
result = tool.browse_url("https://example.com")
```

### Pattern 2: Multi-Tool Workflow
```python
from tools.web_browsing import WebBrowsingTool
from tools.web_to_markdown import WebToMarkdownTool
from tools.bookmarks_manager import BookmarksManagerTool

# Browse -> Convert -> Save
browser = WebBrowsingTool()
converter = WebToMarkdownTool()
bookmarks = BookmarksManagerTool()

page = browser.browse_url("https://example.com")
markdown = converter.convert_url("https://example.com")
bookmarks.add_bookmark("https://example.com", page['title'])
```

### Pattern 3: OpenAI Function Calling
```python
from tools.web_browsing import OPENAI_FUNCTIONS, WebBrowsingTool
import openai

tool = WebBrowsingTool()

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Browse example.com"}],
    functions=OPENAI_FUNCTIONS
)
```

## Selection Guide

### By Use Case

**Web Research**:
- web_browsing (basic)
- web_crawler (advanced)
- bookmarks_manager (organization)

**Content Processing**:
- web_to_markdown (conversion)
- image_analyzer (images)
- file_downloader (files)

**Data Collection**:
- price_data_collector (prices)
- web_crawler (general)
- bookmarks_manager (links)

**Infrastructure**:
- network_monitor (networking)
- system_diagnostics (systems)

### By Complexity

**Beginners**: Start with simple tools
- web_browsing
- file_downloader
- web_to_markdown

**Intermediate**: Add medium complexity
- bookmarks_manager
- image_analyzer
- price_data_collector

**Advanced**: Use complex tools
- web_crawler
- network_monitor
- system_diagnostics

## Portability

All tools are designed to be portable:

✅ **No Cloud Dependencies**: Work offline where possible
✅ **Minimal Requirements**: Only essential libraries
✅ **Cross-Platform**: Windows, macOS, Linux support
✅ **Self-Contained**: No external services required
✅ **Framework Agnostic**: Use with any AI framework

## Safety Features

Every tool includes:
- Input validation
- Error handling
- Timeout protection
- Resource limits
- Secure defaults

## Next Steps

1. **Quick Start**: See [OPENAI_INTEGRATION.md](OPENAI_INTEGRATION.md)
2. **Examples**: Check [examples/](examples/) directory
3. **Tool Docs**: Read individual tool files for API details
4. **Registry**: See [openai_tools/tool_registry.json](openai_tools/tool_registry.json)

---

**Last Updated**: 2025-12-08
**Tools Count**: 9
**Functions Count**: 44
