import re


<<<<<<< HEAD
def split_username(username: str, pattern: str) -> tuple[str, str | None]:
    if re.search(pattern, username):
=======
def split_username(username: str) -> tuple[str, str | None]:
    if re.search(r"^[a-z]+(._)?[a-z0-9]*@[a-z0-9]+(-[a-z0-9]+)*$", username):
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
        username, tenant_slug = username.split("@")
        return username, tenant_slug

    return username, None
