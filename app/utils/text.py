import re


def split_username(username: str) -> tuple[str, str | None]:
    if re.search(r"^[a-z]+(._)?[a-z0-9]*@[a-z0-9]+(-[a-z0-9]+)*$", username):
        username, tenant_slug = username.split("@")
        return username, tenant_slug

    return username, None
