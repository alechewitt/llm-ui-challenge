# LLM UI Challenge

A project that tests how well different large language models can recreate application interfaces from screenshots.

**[View all examples in the full gallery](https://alechewitt.github.io/llm-ui-challenge)**

## About This Project

This project was built using [Claude Code](https://claude.com/claude-code) to benchmark the UI generation capabilities of various frontier LLMs. Each model was given a screenshot of a popular application interface and asked to recreate it in HTML, CSS, and JavaScript.

### The Prompt

Each model received the same simple prompt along with a reference screenshot:

```
Generate this {APPLICATION_NAME} interface in HTML, CSS and JavaScript.
Return a single HTML file with embedded CSS and JavaScript.
```

### Models Tested

- Claude Sonnet 4.5
- Claude Opus 4.5
- GPT-5.1
- GPT-5.1 Codex
- Gemini 2.5 Pro
- Gemini 3 Pro Preview
- Grok 4 Fast
- Qwen3 VL 235B

### Applications

- Microsoft Word
- Jira
- Spotify
- VS Code
- Google Sheets

## Highlights

Here are some of the most impressive outputs from the benchmark:

---

### Microsoft Word - GPT-5.1

**Reference:**

![Microsoft Word Reference](input_screenshots/microsoft_word.png)

**GPT-5.1 Output:**

![GPT-5.1 Microsoft Word](outputs/readme_images/gpt_5_1_ms_word.png)

[View the live HTML](https://alechewitt.github.io/llm-ui-challenge/outputs/microsoft_word/gpt_5_1.html)

This one impressed me with how much actually works. The text formatting buttons are functional, the zoom slider works, and you can change paragraph alignment. That said, it's missing the word count feature that Opus and Gemini both implemented.

---

### Jira - Gemini 3 Pro Preview

**Reference:**

![Jira Reference](input_screenshots/jira.png)

**Gemini 3 Pro Preview Output:**

![Gemini 3 Jira](outputs/readme_images/jira_gemini_3.png)

[View the live HTML](https://alechewitt.github.io/llm-ui-challenge/outputs/jira/gemini_3_pro_preview.html)

This looks almost identical to the real Jira interface. What really stands out is that you can actually drag cards between columns, and there's a nice smooth animation when you do. The card count at the top of each column even updates when you move things around.

---

### Spotify - Gemini 3 Pro Preview

**Reference:**

![Spotify Reference](input_screenshots/spotify.png)

**Gemini 3 Pro Preview Output:**

![Gemini 3 Spotify](outputs/readme_images/spotify_gemini_3_5.png)

[View the live HTML](https://alechewitt.github.io/llm-ui-challenge/outputs/spotify/gemini_3_pro_preview.html)

If it wasn't for the missing album artwork images, I would have been fooled into thinking this was the real Spotify interface. The visual fidelity is remarkably close to the original. Though it's worth noting there isn't any actual functionality or interactive features beyond the appearance.

---

### Google Sheets - Gemini 3 Pro Preview

**Reference:**

![Google Sheets Reference](input_screenshots/google_sheets.png)

**Gemini 3 Pro Preview Output:**

![Gemini 3 Google Sheets](outputs/readme_images/google_sheets_gemini_3.png)

[View the live HTML](https://alechewitt.github.io/llm-ui-challenge/outputs/google_sheets/gemini_3_pro_preview.html)

This is arguably the most impressive output from the entire benchmark. Gemini even implemented the Google Sheets logo as an SVG! You can navigate around the different cells, and it correctly updates the cell reference (like "A1", "B2") when you select a cell. You can type both directly in cells and in the formula bar at the top. The only thing missing is that none of the formatting buttons actually work.

---

## How It Was Built

This entire project was created using Claude Code. You can check out [`initial_prompt.txt`](initial_prompt.txt) to see the original prompt that kicked everything off, along with the resulting [`create_interface.py`](create_interface.py) for calling the OpenRouter API and [`capture_screenshots.py`](capture_screenshots.py) for taking screenshots of the generated HTML pages.

After the initial creation, a few follow-up prompts were needed. Some of the Gemini outputs were getting truncated because OpenRouter was setting a max token limit on the API calls, so those had to be regenerated. There was also a round of regenerating screenshots that were captured at awkward aspect ratios that made them difficult to compare.

## View All Results

Check out the [full gallery](https://alechewitt.github.io/llm-ui-challenge) to see outputs from all models across all applications.
