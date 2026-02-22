---
name: llm-ui-benchmark
description: Benchmark a new LLM model's ability to recreate application UIs from screenshots. Generates HTML for all 5 apps, captures screenshots, and updates the gallery.
argument-hint: <provider/model-name>
---

# LLM UI Benchmark

Benchmark model: **$ARGUMENTS**

Run the full benchmarking pipeline for the given OpenRouter model across all 5 applications.

## Context

This project benchmarks LLMs on their ability to recreate application UIs from screenshots. The model identifier is in OpenRouter format (e.g., `anthropic/claude-opus-4.6`).

### Applications and screenshots

| Application    | Screenshot Path                          |
|----------------|------------------------------------------|
| Microsoft Word | `./input_screenshots/microsoft_word.png` |
| Jira           | `./input_screenshots/jira.png`           |
| Spotify        | `./input_screenshots/spotify.png`        |
| VS Code        | `./input_screenshots/vs_code.png`        |
| Google Sheets  | `./input_screenshots/google_sheets.png`  |

### Screenshot viewport dimensions (width x height)

These MUST be used when capturing screenshots to match the original input aspect ratios:

| Application    | Width | Height |
|----------------|-------|--------|
| Google Sheets  | 2404  | 1126   |
| Jira           | 2048  | 1062   |
| Microsoft Word | 2400  | 1206   |
| Spotify        | 1280  | 980    |
| VS Code        | 1280  | 640    |

### Model name conversion

The model identifier needs conversion for file paths and display:
- **Snake case** (for filenames): strip provider prefix, replace `.` and `-` with `_`, lowercase. E.g., `anthropic/claude-opus-4.6` → `claude_opus_4_6`
- **Display name** (for gallery labels): strip provider prefix, replace `-` with spaces, title case. E.g., `anthropic/claude-opus-4.6` → `Claude Opus 4.6`

Use the `model_to_snake_case` function in `create_interface.py` as the source of truth for the snake_case conversion.

## Step 1: Generate HTML for all 5 applications

Run `create_interface.py` for each application using `uv run`:

```bash
uv run create_interface.py --application_name "APPLICATION" --image_path "./input_screenshots/IMAGE.png" --model "MODEL"
```

Run all 5 applications. If a run fails, log the error and continue with the remaining applications. Runs can be parallelized using backgrounded Bash commands.

## Step 2: Capture screenshots with Playwright MCP

For each successfully generated HTML file:

1. Start a local web server: `python -m http.server 4141` (run in background)
2. For each app, use the Playwright MCP browser tools to:
   a. Resize the browser to match the app's viewport dimensions from the table above
   b. Navigate to `http://localhost:4141/outputs/{app_dir}/{model_snake_case}.html`
   c. Wait for the page to fully load (wait a couple seconds)
   d. Take a screenshot and save it as `outputs/{app_dir}/{model_snake_case}.png`
3. Kill the web server when done

## Step 3: Update index.html

Read the current `index.html` and add a new model card for each application section.

Each application section has a `<div class="model-gallery">` container. Add a new model card at the **end** of each gallery (before the closing `</div>` of `model-gallery`):

```html
                <div class="model-card">
                    <div class="model-label">DISPLAY_NAME</div>
                    <a href="outputs/APP_DIR/MODEL_SNAKE.html" target="_blank" class="model-screenshot">
                        <img src="outputs/APP_DIR/MODEL_SNAKE.png" alt="DISPLAY_NAME output" onerror="this.outerHTML='<div class=placeholder-container>Screenshot not available</div>'">
                    </a>
                </div>
```

The 5 application section IDs in index.html are:
- `microsoft-word`
- `jira`
- `spotify`
- `vs-code`
- `google-sheets`

The corresponding output directory names are:
- `microsoft_word`
- `jira`
- `spotify`
- `vs_code`
- `google_sheets`

**Important:** Only add the model card if it doesn't already exist in that section (check if the model's snake_case filename already appears in the section). If it does already exist, skip that section.

## Step 4: Verify

After all steps, confirm:
- List which HTML files were successfully generated
- List which screenshots were successfully captured
- Confirm index.html was updated
