import os


def get_ca_bundle_path() -> str | bool:
    """Get the CA bundle path.

    Returns:
        str | bool: The path to the CA bundle certificates or False if not found.
    """
    if os.environ.get("REQUESTS_CA_BUNDLE"):
        return os.environ["REQUESTS_CA_BUNDLE"].strip()

    return False
