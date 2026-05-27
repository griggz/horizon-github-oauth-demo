# GitHub Stars MCP Server

Minimal MCP server that pulls repo info (including stars) from GitHub using OAuth. Built to demo Horizon's delegated-auth brokering for downstream platform API calls.

## What it does

One tool: `get_repo_info(owner, repo)` — calls the GitHub API with the authenticated user's token. Works on private repos the user has access to.

## Two ways to run it

### 1. Behind Horizon (default in this repo)

Horizon brokers the full OAuth handshake with GitHub and forwards the access token to the server as an `Authorization: Bearer <token>` header. The server just reads it via `get_http_headers()` — no OAuth code, no client secrets.

Setup:

1. Deploy this server to Horizon.
2. In Horizon → **Settings → Authentication → Link auth source**, create an OAuth source pointing at your GitHub OAuth App's client ID/secret.
3. In your GitHub OAuth App, set the **Authorization callback URL** to whatever `redirect_uri` Horizon sends (grab it from the URL bar on the first auth attempt).
4. Connect an MCP client to the Horizon-hosted URL and authenticate.

### 2. Self-hosted (server owns the OAuth flow)

Uncomment the `GitHubProvider` block in `server.py` and swap the tool body from `get_http_headers()` back to `get_access_token()`. Then:

```bash
uv venv && source .venv/bin/activate
uv pip install -e .

# Create a GitHub OAuth App with callback: http://localhost:8001/auth/callback
cp .env.example .env
# Fill in GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET

source .env
python server.py
```

Server starts on `http://localhost:8001`.

## The OAuth flow

1. MCP client connects to the server (or Horizon gateway).
2. Auth provider redirects to GitHub for authentication (requests `repo` scope).
3. User approves, GitHub returns an access token.
4. Tool uses that token to call `api.github.com`.
5. Returns repo stars, contributor count, visibility, etc.

In Horizon mode, steps 2–3 are brokered by the platform. In self-hosted mode, `GitHubProvider` handles them inside the server.

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
