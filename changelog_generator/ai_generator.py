import json
import logging
import os
from google import genai
from google.genai import types
from google.oauth2 import service_account


def get_prompt(prefix: str) -> str:
    return f"""
Here's a `git diff` between two versions (represented as `git tags`). Write a **concise and precise summary** of this diff using the following structure.
 **Do not introduce new sections** and prioritize **changes** files with this {prefix} over modifications in the common layer.

### Structure:
1. **TL;DR**: A brief, high-impact summary of the most significant changes. Keep it to a few lines.
2. **Functional Changes**: A description of changes **without requiring technical knowledge**, focusing on the impact on services.
3. **Possible Regressions**: Identify concrete risks introduced by the changes. Be precise—avoid generic statements. This section may be used in production incidents, so make it **clear and to the point**.

### Additional Constraints:
- Use **GitHub and Slack-compatible markdown** for readability (e.g., bullet points, bold text, emojis where helpful).
- **No commit-by-commit descriptions**—focus on **high-level themes**.
- **Prioritize clarity over a strict word limit**, but aim for conciseness.
- **Do not infer the release name or version.**
"""


SCOPES = [
    "https://www.googleapis.com/auth/generative-language",
    "https://www.googleapis.com/auth/cloud-platform",
]


def generate_ai_summary(prefix: str| None, git_diff: str | None) -> str | None:
    if not git_diff:
        return "No changes were provided in the diff"

    project = os.getenv("VERTEX_PROJECT")
    location = os.getenv("VERTEX_LOCATION")
    model = os.getenv("VERTEX_MODEL")
    service_account_key = os.getenv("VERTEX_CREDENTIALS")
    prompt = os.getenv("VERTEX_PROMPT", get_prompt(prefix or ""))

    if not project:
        logging.error("Missing VERTEX_PROJECT environment variable")
        return None

    if not location:
        logging.error("Missing VERTEX_LOCATION environment variable")
        return None

    if not model:
        logging.error("Missing VERTEX_MODEL environment variable")
        return None

    if not service_account_key:
        logging.error("Missing VERTEX_CREDENTIALS environment variable")
        return None

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(service_account_key), scopes=SCOPES,
    )
    client = genai.Client(
        vertexai=True,
        project=project,
        location=location,
        credentials=credentials,
    )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(f"{prompt} {git_diff}")],
        )
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
            ),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
    )

    res = []
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        res.append(chunk.text.replace("`", "'"))

    return "".join(res)
