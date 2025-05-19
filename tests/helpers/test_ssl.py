import os

from resnap.helpers.ssl import get_ca_bundle_path


def test_returns_env_var_if_set(monkeypatch) -> None:
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", "/custom/path/to/ca.pem")
    assert get_ca_bundle_path() == "/custom/path/to/ca.pem"


def test_returns_stripped_env_var(monkeypatch) -> None:
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", "   /custom/path/with/spaces.pem   ")
    assert get_ca_bundle_path() == "/custom/path/with/spaces.pem"


def test_returns_false_on_non_posix_os(monkeypatch) -> None:
    monkeypatch.delenv("REQUESTS_CA_BUNDLE", raising=False)
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    assert get_ca_bundle_path() is False
