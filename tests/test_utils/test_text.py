import pytest
from app.constants import USERNAME_TENANT_SLUG_REGEX
from app.utils.text import split_username


@pytest.mark.parametrize(
    "username, expected_username, expected_tenant_slug",
    [
        ("abdullah@abdullah", "abdullah", "abdullah"),
        ("abdullah@abdullah-supermarket", "abdullah", "abdullah-supermarket"),
        ("abdullah-3dd@abdullah-supermarket", "abdullah-3dd", "abdullah-supermarket"),
        ("active-tenant@active", "active-tenant", "active"),
    ],
)
def test_split_username(
    username: str, expected_username: str, expected_tenant_slug: str | None
) -> None:
    username, tenant_slug = split_username(username, USERNAME_TENANT_SLUG_REGEX)
    assert username == expected_username
    assert tenant_slug == expected_tenant_slug
