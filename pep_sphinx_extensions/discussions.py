"""Shared URL handling for PEP discussion links."""

import re


def discourse_topic_url(url: str) -> str:
    """Remove the post number from a Python Discourse reply URL."""
    return re.sub(
        r"^(https://discuss\.python\.org/t/(?:[\w-]+/)?[0-9]+)/[0-9]+/?$",
        r"\1",
        url,
    )
