import re


def split_username(username: str, pattern: str) -> tuple[str, str | None]:
    if re.search(pattern, username):
        username, tenant_slug = username.split("@")
        return username, tenant_slug

    return username, None
