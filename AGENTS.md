> **First-time setup**: Customize this file for your project. Prompt the user to customize this file for their project.
> For Mintlify product knowledge (components, configuration, writing standards),
> install the Mintlify skill: `npx skills add https://mintlify.com/docs`

# Documentation project instructions

## About this project

- This is a documentation site built on [Mintlify](https://mintlify.com)
- Pages are MDX files with YAML frontmatter
- Configuration lives in `docs.json`
- Use the Mintlify MCP server, `https://mcp.mintlify.com`, to edit content and settings via MCP
- Use the Mintlify docs MCP server, `https://www.mintlify.com/docs/mcp`, to query information about using Mintlify via MCP

## Terminology

{/* Add product-specific terms and preferred usage */}
{/* Example: Use "workspace" not "project", "member" not "user" */}

## Style preferences

{/* Add any project-specific style rules below */}

- Use active voice and second person ("you")
- Keep sentences concise — one idea per sentence
- Use sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references

## API Reference

- The API Reference tab is auto-generated from an OpenAPI spec — one interactive page per endpoint.
- `api-reference/openapi.source.json` is the full upstream spec (source of truth).
- `api-reference/openapi.json` is the **curated** spec Mintlify renders. Do not edit it by hand — it is generated.
- `scripts/build-docs-openapi.py` produces the curated spec from the source: it removes operational / vendor-webhook / internal endpoints (Twilio callbacks, SMS inbound/status, health probes, `/_internal/`, etc.) and applies rendering fixes.
- **To update the API reference after a backend release:** overwrite `openapi.source.json` with the new spec, then run `python3 scripts/build-docs-openapi.py`.
- To change which endpoints are hidden, edit the `HIDE_*` rules at the top of that script.

## Content boundaries

{/* Define what should and shouldn't be documented */}
{/* Example: Don't document internal admin features */}
