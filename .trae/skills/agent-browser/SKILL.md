---
name: agent-browser
description: Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to interact with websites, test web applications, or extract data from web pages.
---

# Agent Browser

This skill provides browser automation capabilities for Claude, allowing it to interact with websites, test web applications, and extract data from web pages.

## When to Use This Skill

Use this skill when the user:
- Needs to test web applications or websites
- Wants to fill out forms automatically
- Needs to take screenshots of web pages
- Wants to extract data from web pages
- Needs to automate web-based workflows
- Asks about browser automation or web testing

## Core Capabilities

- **Web Navigation**: Open URLs and navigate between pages
- **Form Filling**: Automatically fill out web forms
- **Screenshots**: Capture screenshots of web pages
- **Data Extraction**: Extract text, tables, and other data from web pages
- **Browser Control**: Control browser behavior and settings

## Usage Examples

### Example 1: Taking a screenshot
```
agent-browser open https://example.com
agent-browser screenshot output.png
```

### Example 2: Filling a form
```
agent-browser open https://example.com/login
agent-browser fill #username "user123"
agent-browser fill #password "password123"
agent-browser click #login-button
```

### Example 3: Extracting data
```
agent-browser open https://example.com/data
agent-browser extract .table-class
```

## Browser Modes

The agent-browser supports three browser modes:
1. **Headless Chromium** - Headless mode for automated tasks
2. **Real Browser** - Full browser with GUI for interactive testing
3. **Remote Browser** - Connect to a remote browser instance

## Dependencies

- Playwright or Puppeteer for browser automation
- Node.js runtime environment
- Appropriate browser drivers (Chrome, Firefox, etc.)

## Installation

To install this skill:
```bash
npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser
```

## Best Practices

- Always specify clear objectives for browser automation
- Use appropriate selectors for web elements
- Handle pagination and dynamic content appropriately
- Respect website terms of service and robots.txt
- Use headless mode for automated tasks to save resources
