"""Document feature constants."""

from typing import Any

# Metadata keys that are safe to return to the user.
# Internal/debug keys (raw_text, service, id_extraction_method, llm_error, filename, etc.)
# are excluded by only including this allowlist.
USER_FACING_METADATA_KEYS = frozenset({
    "first_name",
    "last_name",
    "date_of_birth",
    "expiry_date",
    "issue_date",
    "address",
    "sex",
    "issuing_authority",
    "nationality",
    "place_of_birth",
})


def filter_metadata_for_user(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """
    Return only user-facing metadata keys.
    
    Strips internal fields (raw_text, service, id_extraction_method, llm_error,
    filename, content_type, size_bytes, llm_parsing, etc.) so they are never
    returned to the client.
    """
    if not metadata:
        return {}
    return {k: v for k, v in metadata.items() if k in USER_FACING_METADATA_KEYS}
