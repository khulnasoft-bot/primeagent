import pytest
from wfx_rea.client import ReaAuthorizationError, authorize_target_path


def test_authorize_target_path_accepts_files_within_an_allowed_root(tmp_path):
    target = tmp_path / "sample.bin"
    target.write_bytes(b"fixture")

    assert authorize_target_path(str(target), str(tmp_path)) == target.resolve()


def test_authorize_target_path_rejects_targets_outside_allowed_roots(tmp_path):
    allowed = tmp_path / "allowed"
    denied = tmp_path / "denied"
    allowed.mkdir()
    denied.mkdir()
    target = denied / "sample.bin"
    target.write_bytes(b"fixture")

    with pytest.raises(ReaAuthorizationError, match="outside"):
        authorize_target_path(str(target), str(allowed))


def test_authorize_target_path_fails_closed_without_configured_roots(tmp_path):
    target = tmp_path / "sample.bin"
    target.write_bytes(b"fixture")

    with pytest.raises(ReaAuthorizationError, match="REA_ALLOWED_TARGET_ROOTS"):
        authorize_target_path(str(target), "")


def test_authorize_target_path_rejects_directory_symlinks(tmp_path):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "secret.bin").write_bytes(b"not authorized")
    (root / "linked").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ReaAuthorizationError, match="symlinks"):
        authorize_target_path(str(root), str(tmp_path))


def test_authorize_target_path_bounds_directory_entry_count(monkeypatch, tmp_path):
    target = tmp_path / "tree"
    target.mkdir()
    (target / "one.bin").write_bytes(b"fixture")
    monkeypatch.setenv("REA_MAX_TARGET_ENTRIES", "1")

    with pytest.raises(ReaAuthorizationError, match="entry limit"):
        authorize_target_path(str(target), str(tmp_path))
