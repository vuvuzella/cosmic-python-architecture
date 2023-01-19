import shutil
import tempfile
import pytest
from pathlib import Path
from sync import sync, determine_actions
from typing import Dict


@pytest.fixture
def create_temp_fs():
    source, dest = tempfile.mkdtemp(), tempfile.mkdtemp()

    yield source, dest

    shutil.rmtree(source)
    shutil.rmtree(dest)


def test_when_a_file_exists_in_source_but_not_in_destination(create_temp_fs):
    source, dest = create_temp_fs

    print(f"source: {source}")
    print(f"dest: {dest}")

    source = tempfile.mkdtemp()
    dest = tempfile.mkdtemp()

    fn = "new-file.txt"

    content = "Hello Source World"
    (Path(source) / fn).write_text(content)

    sync(source, dest)

    expected_path = Path(dest) / fn
    assert expected_path.exists()
    assert expected_path.read_text() == content


def test_when_a_file_has_been_renamed_in_source():
    source: str = ""
    dest: str = ""
    try:
        source = tempfile.mkdtemp()
        dest = tempfile.mkdtemp()
        fn1 = "source-file.txt"
        fn2 = "destination-file.txt"
        content = "Hello Same Content"

        (Path(source) / fn1).write_text(content)
        (Path(dest) / fn2).write_text(content)

        sync(source, dest)

        expected_path = Path(dest) / fn1
        assert expected_path.exists()
        assert expected_path.read_text() == content

    finally:
        shutil.rmtree(source)
        shutil.rmtree(dest)


def test_file_exists_in_source_simplified():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {}
    actions = list(
        determine_actions(source_hashes, dest_hashes, Path("/src"), Path("/dest"))
    )
    assert actions == [("COPY", Path("/src/fn1"), Path("/dest/fn1"))]


def test_file_renamed_simplified():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {"hash1": "fn2"}
    actions = list(
        determine_actions(source_hashes, dest_hashes, Path("/src"), Path("/dest"))
    )
    assert actions == [("MOVE", Path("/dest/fn2"), Path("/dest/fn1"))]


class FakeFileSystem:
    def __init__(self, path_hashes) -> None:
        self.path_hashes = path_hashes
        self.actions = []

    def read(self, path) -> Dict[str, str]:
        return self.path_hashes[path]

    def copy(self, source, destination):
        self.actions.append(("COPY", source, destination))

    def move(self, source, destination):
        self.actions.append(("MOVE", source, destination))

    def remove(self, path):
        self.actions.append(("DELETE", path, None))


def test_file_exists_in_source_but_not_in_destination_fakefs():
    fake_fs = FakeFileSystem({"/src": {"hash1": "fn1"}, "/dst": {}})

    sync("/src", "/dst", fake_fs)

    assert fake_fs.actions == [("COPY", Path("/src/fn1"), Path("/dst/fn1"))]


def test_file_renamed_fakefs():
    fake_fs = FakeFileSystem({"/src": {"hash1": "fn1"}, "/dst": {"hash1": "fn2"}})

    sync("/src", "/dst", fake_fs)

    assert fake_fs.actions == [("MOVE", Path("/dst/fn2"), Path("/dst/fn1"))]
