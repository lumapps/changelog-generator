import os
from google import genai
from google.genai import types

PROMPT = (
    "Here's a git diff between two versions (represented as git tags). "
    "Write a summary of this diff by following this structure. "
    "A TL;DR section with very few lines expressing the salient points of your analysis "
    "A Functional Changes section that should be understandable by readers that have no technical knowledge "
    "A section about possible regressions that could appear : this section should aim to be brief as it might be used during a production incident, but it musn't be too generic either"
    "A section about key kong/log metrics that should be observed during the production release process, these must be very precise"
    "The summary must be written with markdown. It should be pleasing and give priority to salient points, must use colors and must use tasteful fonts, and follow best practices. You can use UML schemas and diagrams."
)


def generate_ai_summary(git_diff: str | None) -> str | None:
    if not git_diff:
        return None

    project = os.getenv("VERTEX_PROJECT")
    location = os.getenv("VERTEX_LOCATION")
    model = os.getenv("VERTEX_MODEL")
    credentials = os.getenv("VERTEX_CREDENTIALS")

    if not all([project, location, model, credentials]):
        return None

    client = genai.Client(
        vertexai=True,
        project=project,
        location=location,
        credentials=credentials,
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    f"{PROMPT} {git_diff}"
                )
            ],
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
        res.append(chunk.text)

    return "".join(res)
