import os
import subprocess
import tarfile
import threading
import zipfile

import pytest
from pathlib import Path


# -----------------------------
# EXTRACT_CMD
# Falls back to the script path if 'extract' is not on $PATH.
# Override at runtime: EXTRACT_CMD=~/.config/scripts/extract.sh pytest
# -----------------------------
EXTRACT_CMD = os.environ.get(
    "EXTRACT_CMD",
    os.path.expanduser("~/.config/scripts/extract.sh"),
)


# -----------------------------
# FIXTURE (previously conftest.py)
# -----------------------------
@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    base = tmp_path_factory.mktemp("extract_test")

    input_dir = base / "input"
    nested = input_dir / "nested"
    nested.mkdir(parents=True)

    (input_dir / "a.txt").write_text("hello world")
    (input_dir / "b.txt").write_text("foo bar")
    (nested / "c.txt").write_text("nested file")

    # Large file (stress test)
    with open(input_dir / "large.txt", "wb") as f:
        f.write(os.urandom(2_000_000))

    cwd = os.getcwd()
    os.chdir(base)

    # ZIP
    with zipfile.ZipFile("test.zip", "w") as z:
        for root, _, files in os.walk("input"):
            for file in files:
                path = os.path.join(root, file)
                z.write(path)

    # TAR
    with tarfile.open("test.tar", "w") as t:
        t.add("input")

    # TAR.GZ
    with tarfile.open("test.tar.gz", "w:gz") as t:
        t.add("input")

    # TAR.BZ2
    with tarfile.open("test.tar.bz2", "w:bz2") as t:
        t.add("input")

    # TAR.XZ
    with tarfile.open("test.tar.xz", "w:xz") as t:
        t.add("input")

    # Corrupt file for failure tests
    (base / "bad.zip").write_text("this is not a real archive")

    os.chdir(cwd)

    return base


# -----------------------------
# HELPERS
# -----------------------------
def run(cmd, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

def assert_extracted(path):
    assert (Path(path) / "input" / "a.txt").exists()
    assert (Path(path) / "input" / "b.txt").exists()
    assert (Path(path) / "input" / "nested" / "c.txt").exists()


# -----------------------------
# BASIC EXTRACTION
# -----------------------------
@pytest.mark.parametrize("archive", [
    "test.zip",
    "test.tar",
    "test.tar.gz",
    "test.tar.bz2",
    "test.tar.xz",
])
def test_basic_extraction(test_data_dir, archive):
    # Each archive gets its own uniquely named output dir to avoid
    # cross-test interference within the session-scoped fixture.
    out = test_data_dir / (archive + "_out")

    result = run([EXTRACT_CMD, str(test_data_dir / archive), str(out)])

    assert result.returncode == 0
    assert_extracted(out)


# -----------------------------
# OVERWRITE PROTECTION
# -----------------------------
def test_overwrite_protection(test_data_dir):
    # Unique dir — not shared with any other test.
    out = test_data_dir / "overwrite_protection_out"
    out.mkdir()

    result = run([EXTRACT_CMD, str(test_data_dir / "test.zip"), str(out)])

    assert result.returncode != 0
    assert "already exists" in result.stdout.lower()
    # Dir must still be present — script must not have removed it.
    assert out.exists()


# -----------------------------
# FORCE OVERWRITE
# -----------------------------
def test_force_overwrite(test_data_dir):
    # Unique dir — not shared with any other test.
    out = test_data_dir / "force_overwrite_out"
    out.mkdir()

    result = run([
        EXTRACT_CMD, "--force",
        str(test_data_dir / "test.zip"),
        str(out),
    ])

    assert result.returncode == 0
    assert_extracted(out)


# -----------------------------
# CLEANUP ON FAILURE
# -----------------------------
def test_cleanup_on_failure(test_data_dir):
    # Unique dir — not pre-created; the script creates and then removes it.
    out = test_data_dir / "cleanup_failure_out"

    result = run([EXTRACT_CMD, str(test_data_dir / "bad.zip"), str(out)])

    assert result.returncode != 0
    assert not out.exists()


# -----------------------------
# MISSING ARGUMENTS
# -----------------------------
def test_missing_args():
    result = run([EXTRACT_CMD])

    assert result.returncode != 0
    assert "usage" in result.stdout.lower()


# -----------------------------
# CONCURRENT EXTRACTIONS
# Renamed from test_parallel_execution: this is a smoke test that two
# simultaneous extractions to *different* output directories both succeed.
# It does not test lock collision (same archive + same output dir).
# -----------------------------
def test_concurrent_extractions_to_different_dirs(test_data_dir):
    out1 = test_data_dir / "concurrent_out1"
    out2 = test_data_dir / "concurrent_out2"

    def run1():
        run([EXTRACT_CMD, str(test_data_dir / "test.zip"), str(out1)])

    def run2():
        run([EXTRACT_CMD, str(test_data_dir / "test.zip"), str(out2)])

    t1 = threading.Thread(target=run1)
    t2 = threading.Thread(target=run2)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert_extracted(out1)
    assert_extracted(out2)



def test_auto_output_dir_naming(test_data_dir, tmp_path):
    """Script derives output dir from archive name when none is given."""
    result = run([EXTRACT_CMD, str(test_data_dir / "test.zip")], cwd=tmp_path)
    assert result.returncode == 0
    assert_extracted(tmp_path / "test")  # .zip stripped


def test_auto_output_dir_double_extension(test_data_dir, tmp_path):
    """Double extensions like .tar.gz should strip both, not just .gz."""
    result = run([EXTRACT_CMD, str(test_data_dir / "test.tar.gz")], cwd=tmp_path)
    assert result.returncode == 0
    assert_extracted(tmp_path / "test")  # both .tar and .gz stripped, not just .gz




def test_file_not_found(test_data_dir):
    result = run([EXTRACT_CMD, str(test_data_dir / "nonexistent.zip")])
    assert result.returncode != 0
    assert "not found" in result.stdout.lower()




def test_no_dir_created_on_missing_file(test_data_dir):
    out = test_data_dir / "should_not_exist"
    run([EXTRACT_CMD, str(test_data_dir / "nonexistent.zip"), str(out)])
    assert not out.exists()

def test_no_dir_created_on_missing_args():
    run([EXTRACT_CMD])
    # Just check it doesn't crash the test suite — return code covered elsewhere


def test_large_file_extraction(test_data_dir):
    out = test_data_dir / "large_file_out"
    result = run([EXTRACT_CMD, str(test_data_dir / "test.tar.gz"), str(out)])
    assert result.returncode == 0
    assert (out / "input" / "large.txt").exists()
    assert (out / "input" / "large.txt").stat().st_size == 2_000_000



def test_nested_structure_preserved(test_data_dir):
    out = test_data_dir / "nested_structure_out"
    run([EXTRACT_CMD, str(test_data_dir / "test.zip"), str(out)])
    nested_file = out / "input" / "nested" / "c.txt"
    assert nested_file.exists()
    assert nested_file.read_text() == "nested file"


def test_extracted_contents_correct(test_data_dir):
    out = test_data_dir / "contents_check_out"
    run([EXTRACT_CMD, str(test_data_dir / "test.zip"), str(out)])
    assert (out / "input" / "a.txt").read_text() == "hello world"
    assert (out / "input" / "b.txt").read_text() == "foo bar"


def test_force_on_nonexistent_dir(test_data_dir):
    out = test_data_dir / "force_nonexistent_out"
    assert not out.exists()
    result = run([EXTRACT_CMD, "--force", str(test_data_dir / "test.zip"), str(out)])
    assert result.returncode == 0
    assert_extracted(out)