from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import UploadFile


def build_output_path(output_dir: Path, source_name: str, suffix: str) -> Path:
    source_path = Path(source_name)
    stem = source_path.stem or 'result'
    extension = source_path.suffix or '.jpg'
    filename = f'{stem}{suffix}{extension}'
    return output_dir / filename


async def save_upload_file(upload_file: UploadFile, destination_dir: Path) -> tuple[Path, str]:
    destination_dir.mkdir(parents=True, exist_ok=True)
    original_name = upload_file.filename or f'{uuid4().hex}.bin'
    source_path = Path(original_name)
    suffix = source_path.suffix or '.bin'
    file_path = destination_dir / f'{source_path.stem}_{uuid4().hex}{suffix}'
    with file_path.open('wb') as buffer:
        upload_file.file.seek(0)
        copyfileobj(upload_file.file, buffer)
    return file_path, original_name
