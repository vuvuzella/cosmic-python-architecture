import hashlib
import os
import argparse
import shutil

from pathlib import Path
from typing import Dict, Tuple, Generator

BLOCKSIZE = 65536


def hash_file(file_path: str) -> str:
    hasher = hashlib.sha1()
    with open(file_path, "rb") as f:
        buf = f.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


def read_paths_and_hashes(root) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            rel_path = Path(folder) / fn
            hashes[hash_file(rel_path)] = fn
    print(hashes)
    return hashes


def determine_actions(
    source_hashes: Dict[str, str],
    destination_hashes: Dict[str, str],
    source: str,
    destination: str,
) -> Generator[Tuple[str, str, str | None], None, None]:
    for sha, fn in source_hashes.items():
        if sha not in destination_hashes:
            source_path = Path(source) / fn
            destination_path = Path(destination) / fn
            yield ("COPY", str(source_path), str(destination_path))
        elif destination_hashes[sha] != fn:
            old_destination_path = Path(destination) / destination_hashes[sha]
            new_destination_path = Path(destination) / fn
            yield ("MOVE", str(old_destination_path), str(new_destination_path))

    for sha, fn in destination_hashes.items():
        if sha not in source_hashes:
            yield ("DELETE", str(Path(destination) / fn), None)


class FileSystem:
    def __init__(self) -> None:
        pass

    def read(self, path) -> Dict[str, str]:
        return read_paths_and_hashes(path)

    def copy(self, source, destination):
        shutil.copyfile(source, destination)

    def move(self, source, destination):
        shutil.move(source, destination)

    def remove(self, path):
        os.remove(path)


def sync(source_path: str, destination_path: str, filesystem=FileSystem()):
    # Walk the source folder and build  a dict of filenames and their hashes
    # TODO: make the sync work with nested file structure
    # source_hashes = {}

    # for dirpath, dirnames, filenames in os.walk(source_path):
    #     for fn in filenames:
    #         source_hashes[hash_file(Path(dirpath) / fn)] = fn

    # seen = set()

    # for dirpath, dirnames, filenames in os.walk(destination_path):
    #     for fn in filenames:
    #         dest_path = Path(dirpath) / fn
    #         dest_hash = hash_file(dest_path)
    #         seen.add(dest_hash)

    #         if dest_hash not in source_hashes:
    #             dest_path.unlink()

    #         elif dest_hash in source_hashes and fn != source_hashes[dest_hash]:
    #             shutil.move(dest_path, Path(dirpath) / source_hashes[dest_hash])

    # for source_hash, fn in source_hashes.items():
    #     if source_hash not in seen:
    #         shutil.copy(Path(source_path) / fn, Path(destination_path) / fn)

    # source_hashes = read_paths_and_hashes(source_path)
    # dest_hashes = read_paths_and_hashes(destination_path)

    source_hashes = filesystem.read(source_path)
    dest_hashes = filesystem.read(destination_path)

    actions = determine_actions(
        source_hashes, dest_hashes, source_path, destination_path
    )

    for action, *paths in actions:
        if action == "COPY":
            # shutil.copyfile(*paths)
            filesystem.copy(*paths)
        elif action == "MOVE":
            # shutil.move(*paths)
            filesystem.move(*paths)
        elif action == "DELETE":
            # os.remove(paths[0])
            filesystem.remove(paths[0])


def main():
    arg_parser = argparse.ArgumentParser(
        "SyncRo", "A program that synchronizes two folders", "-h for help"
    )
    arg_parser.add_argument("source")
    arg_parser.add_argument("destination")
    args = arg_parser.parse_args()
    source_arg: str = args.source
    source_arg = source_arg.replace("./", "")
    destination_arg: str = args.destination
    destination_arg = destination_arg.replace("./", "")
    source_path = f"{os.path.abspath(os.getcwd())}/{source_arg}"
    destination_path = f"{os.path.abspath(os.getcwd())}/{destination_arg}"

    sync(source_path, destination_path)

    print(source_path)
    print(destination_path)


if __name__ == "__main__":
    main()
