from pathlib import Path

from .output_directory import create_output_directory


def test_directory_exists_when_if_not_empty(tmp_path: Path):
    with create_output_directory(tmp_path / "tmp_dir") as output_dir:
        _save_file(output_dir / "file.txt")

    assert output_dir.exists()


def _save_file(file_path: Path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("")


def test_directory_not_exists_if_empty(tmp_path: Path):
    with create_output_directory(tmp_path / "tmp_dir") as output_dir:
        pass

    assert not output_dir.exists()
