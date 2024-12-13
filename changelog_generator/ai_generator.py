import json
import logging
import os
from google import genai
from google.genai import types
from google.oauth2 import service_account

PROMPT = (
    "Here's a git diff between two versions (represented as git tags). "
    "Write a summary of this diff by following this structure "
    "A TL;DR section with very few lines expressing the salient points of your analysis "
    "A Functional Changes section that should be understandable by readers that have no technical knowledge "
    "A section about possible regressions that could appear : this section should aim to be brief as it might be used during a production incident, but it musn't be too generic either"
    "A section about key kong/log metrics that should be observed during the production release process, these must be very precise"
    "The summary must be written with github and slack compatible markdown. It should be pleasing and give priority to salient points, must use colors and must use tasteful fonts, and follow best practices. You can use UML schemas and diagrams."
    "Do not print a description of each commit, the goal is to be as concise as possible. Do not take more than 200 words."
)

SCOPES = [
    "https://www.googleapis.com/auth/generative-language",
    "https://www.googleapis.com/auth/cloud-platform",
]


def generate_ai_summary(git_diff: str | None) -> str | None:
    if not git_diff:
        return "No changes were provided in the diff"

    project = os.getenv("VERTEX_PROJECT")
    location = os.getenv("VERTEX_LOCATION")
    model = os.getenv("VERTEX_MODEL")
    service_account_key = os.getenv("VERTEX_CREDENTIALS")
    prompt = os.getenv("VERTEX_PROMPT", PROMPT)

    if not project:
        logging.error("Missing VERTEX_PROJECT environment variable")

    if not location:
        logging.error("Missing VERTEX_LOCATION environment variable")

    if not model:
        logging.error("Missing VERTEX_MODEL environment variable")

    if not service_account_key:
        logging.error("Missing VERTEX_CREDENTIALS environment variable")

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
