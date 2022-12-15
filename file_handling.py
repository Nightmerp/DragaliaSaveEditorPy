# file_handling.py

from pathlib import Path
import shutil

class CopyFileError(Exception):
    pass

def find_file(path: str | Path) -> 'File Path':
    try:
        file_path = Path(path)
        if file_path.is_file():
            return file_path
    except:
        pass
    
    return None

def find_directory(path: str | Path) -> 'File Directory':
    try:
        directory_path = Path(path)
        if directory_path.is_dir():
            return directory_path
    except:
        pass

    return None

def get_file_name(path: Path) -> str:
    return path.name

def get_parent_directory(path: Path) -> Path:
    return path.parent

def copy_file(source: Path, destination: Path) -> None:
    try:
        shutil.copyfile(source, destination)
    except:
        raise CopyFileError
