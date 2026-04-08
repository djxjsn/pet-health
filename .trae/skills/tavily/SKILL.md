---
name: tavily
description: AI-optimized web search using Tavily Search API. Use when you need comprehensive web research, current events lookup, domain-specific search, or AI-generated answers based on web data.
---

# Tavily

This skill provides AI-optimized web search capabilities using the Tavily Search API, enabling Claude to perform comprehensive web research and retrieve current information.

## When to Use This Skill

Use this skill when the user:
- Needs current information beyond the training data
- Wants to research specific topics or domains
- Needs to verify facts or statistics
- Asks about recent events or news
- Requires domain-specific information
- Wants AI-generated answers based on web data

## Core Capabilities

- **Web Search**: Perform AI-optimized web searches
- **Current Information**: Retrieve up-to-date information
- **Domain-Specific Search**: Focus on specific domains or industries
- **AI-Generated Answers**: Get summarized answers based on web data
- **Citation Support**: Include sources for information retrieved
- **Search Depth Control**: Adjust search depth for different needs

## Search Depth Options

- **Fast**: Quick search with basic results (suitable for simple queries)
- **Ultra-fast**: Minimal search for immediate answers
- **Comprehensive**: In-depth search with multiple sources

## Usage Examples

### Example 1: Basic search
```python
from tavily import TavilyClient

client = TavilyClient(api_key='YOUR_API_KEY')
results = client.search('latest AI trends 2026')
print(results)
```

### Example 2: Domain-specific search
```python
results = client.search(
    'machine learning best practices',
    domain='tech'
)
```

### Example 3: AI-generated answer
```python
answer = client.search(
    'What is the current state of quantum computing?',
    include_answer=True
)
print(answer['answer'])
```

### Example 4: Adjusting search depth
```python
results = client.search(
    'climate change effects',
    search_depth='comprehensive'
)
```

## Integration with Anthropic Claude

To integrate Tavily with Claude using tool calling:

```python
import anthropic
import os
from tavily import TavilyClient

# Set up API keys
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
TAVILY_API_KEY = os.environ['TAVILY_API_KEY']

# Initialize clients
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# Tool schema
tools = [
    {
        "name": "tavily_search",
        "description": "Search the web for current information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["fast", "ultra-fast", "comprehensive"],
                    "default": "fast"
                }
            },
            "required": ["query"]
        }
    }
]

# System prompt
system_prompt = "You are a helpful assistant with access to web search capabilities. Use the tavily_search tool when you need current information."

# Main chat function
def chat_with_search(message):
    response = claude.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
        tools=tools
    )
    
    if response.stop_reason == "tool_use":
        tool_call = response.content[0].tool_use
        if tool_call.name == "tavily_search":
            query = tool_call.input["query"]
            search_depth = tool_call.input.get("search_depth", "fast")
            
            # Execute search
            search_results = tavily.search(query, search_depth=search_depth)
            
            # Continue the conversation with search results
            response = claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "tool",
                        "name": "tavily_search",
                        "content": str(search_results)
                    }
                ]
            )
    
    return response.content[0].text

# Usage example
result = chat_with_search("What are the latest developments in AI as of 2026?")
print(result)
```

## Installation

To install the Tavily client:
```bash
pip install tavily-python
```

## API Key Setup

1. Sign up for a Tavily API key at https://tavily.com
2. Set the API key as an environment variable:
   ```bash
   # Linux/Mac
   export TAVILY_API_KEY=your_api_key
   
   # Windows
   set TAVILY_API_KEY=your_api_key
   ```

## Best Practices

- Use specific and clear search queries
- Choose the appropriate search depth based on your needs
- Always cite sources when using information from Tavily
- Verify critical information from multiple sources
- Respect API rate limits and usage guidelines
- Use domain-specific searches for more relevant results
