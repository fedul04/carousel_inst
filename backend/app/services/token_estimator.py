import re


def estimate_tokens(*chunks: str | None) -> int:
    text = "\n".join(chunk for chunk in chunks if chunk)
    words = len(re.findall(r"\w+", text, flags=re.UNICODE))
    return max(300, int(words * 1.6) + 150)

