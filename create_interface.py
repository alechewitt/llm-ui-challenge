#!/usr/bin/env python3
"""
Script to call OpenRouter API with multimodal prompts to recreate application interfaces.
"""

import argparse
import base64
import os
import re
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv


def get_api_key() -> str:
    """Get OpenRouter API key from environment variables."""
    # Load .env from the script's directory
    script_dir = Path(__file__).parent
    load_dotenv(script_dir / ".env")
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPEN_ROUTER_KEY") or os.environ.get("OPEN_ROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY or OPEN_ROUTER_KEY environment variable not set")
    return key


def model_to_snake_case(model: str) -> str:
    """Convert model identifier to snake_case filename.

    Example: anthropic/claude-sonnet-4.5 -> claude_sonnet_4_5
    """
    # Remove provider prefix (everything before /)
    name = model.split("/")[-1]
    # Replace dots, hyphens with underscores
    name = re.sub(r"[.\-]", "_", name)
    # Remove any non-alphanumeric characters except underscores
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)
    return name.lower()


def app_name_to_dir(app_name: str) -> str:
    """Convert application name to directory name.

    Example: Microsoft Word -> microsoft_word
    """
    return app_name.lower().replace(" ", "_")


def encode_image(image_path: str) -> tuple[str, str]:
    """Encode image to base64 and determine media type."""
    path = Path(image_path)
    suffix = path.suffix.lower()

    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    media_type = media_types.get(suffix, "image/png")

    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    return data, media_type


def extract_html(response_text: str) -> str:
    """Extract HTML code from response, stripping markdown code fences."""
    # Try to find HTML in code blocks first
    patterns = [
        r"```html\s*([\s\S]*?)```",  # ```html ... ```
        r"```\s*(<!DOCTYPE[\s\S]*?)```",  # ``` <!DOCTYPE ... ```
        r"```\s*(<html[\s\S]*?)```",  # ``` <html ... ```
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # If no code block found, check if response is raw HTML
    if response_text.strip().startswith(("<!DOCTYPE", "<html", "<HTML")):
        return response_text.strip()

    # Last resort: return as-is
    return response_text.strip()


def call_openrouter(
    api_key: str,
    model: str,
    app_name: str,
    image_data: str,
    media_type: str,
    max_retries: int = 3,
) -> str:
    """Call OpenRouter API with the multimodal prompt."""
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/benchmarking",
        "X-Title": "LLM Interface Benchmark",
    }

    prompt = f"""Generate this {app_name} interface in HTML, CSS and JavaScript.
Return a single HTML file with embedded CSS and JavaScript."""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}",
                        },
                    },
                ],
            }
        ],
        "max_tokens": 16000,
    }

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=300.0) as client:
                response = client.post(url, headers=headers, json=payload)

                if response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 2 ** attempt * 10  # Exponential backoff: 10, 20, 40 seconds
                    print(f"  Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()

                if "error" in data:
                    raise ValueError(f"API error: {data['error']}")

                content = data["choices"][0]["message"]["content"]
                return content

        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt * 5
                print(f"  Timeout. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait_time = 2 ** attempt * 10
                print(f"  Rate limited (HTTP 429). Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            raise

    raise RuntimeError(f"Failed after {max_retries} retries")


def main():
    parser = argparse.ArgumentParser(
        description="Generate UI interface using OpenRouter LLM API"
    )
    parser.add_argument(
        "--application_name",
        required=True,
        help="Name of the application (e.g., 'Microsoft Word')",
    )
    parser.add_argument(
        "--image_path",
        required=True,
        help="Path to the screenshot file",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="OpenRouter model identifier (e.g., 'anthropic/claude-sonnet-4.5')",
    )

    args = parser.parse_args()

    # Validate image exists
    if not Path(args.image_path).exists():
        print(f"Error: Image file not found: {args.image_path}")
        return 1

    # Get API key
    try:
        api_key = get_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Prepare output path
    app_dir = app_name_to_dir(args.application_name)
    model_name = model_to_snake_case(args.model)
    output_dir = Path("outputs") / app_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{model_name}.html"

    print(f"Processing: {args.application_name} with {args.model}")
    print(f"  Image: {args.image_path}")
    print(f"  Output: {output_file}")

    try:
        # Encode image
        image_data, media_type = encode_image(args.image_path)

        # Call API
        print("  Calling OpenRouter API...")
        response = call_openrouter(
            api_key=api_key,
            model=args.model,
            app_name=args.application_name,
            image_data=image_data,
            media_type=media_type,
        )

        # Extract HTML
        html_content = extract_html(response)

        # Save output
        output_file.write_text(html_content)
        print(f"  Success! Saved to {output_file}")
        return 0

    except Exception as e:
        print(f"  Error with {args.model}: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
