import pytest
import os
import shutil
import tarfile
import zipfile

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

    # Helper function
    def make_archives():
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

        # Corrupt file
        (base / "bad.zip").write_text("this is not a real archive")

        os.chdir(cwd)

    make_archives()

    return base