# GitHub Stars MCP Server

Minimal MCP server that pulls repo info (including stars) from GitHub using OAuth. Built to test Horizon's OAuth brokering for downstream platform API calls.

## What it does

One tool: `get_repo_info(owner, repo)` -- calls the GitHub API with the authenticated user's token. Works on private repos the user has access to.

## Setup

```bash
# Install
uv venv && source .venv/bin/activate
uv pip install -e .

# Configure (create a GitHub OAuth App first)
# Callback URL: http://localhost:8001/auth/callback
cp .env.example .env
# Fill in GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET

# Run
source .env
python server.py
```

Server starts on `http://localhost:8001`. Connect any MCP client and authenticate via GitHub OAuth.

## The OAuth flow

1. MCP client connects to server
2. Server redirects to GitHub for authentication (requests `repo` scope)
3. User approves, GitHub returns access token
4. Tool uses that token to call `api.github.com`
5. Returns repo stars, contributor count, visibility, etc.

When deployed to Horizon, step 2-3 is brokered by the platform instead of handled by this server directly.

## Example output

```json
{
  "name": "PrefectHQ/prefect",
  "stars": 18245,
  "private": false,
  "description": "Prefect is a workflow orchestration framework...",
  "language": "Python",
  "forks": 1289,
  "contributors": 30,
  "default_branch": "main"
}
```
