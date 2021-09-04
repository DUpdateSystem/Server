import tarfile
import tempfile
from io import BytesIO


def zip_raw(value, file_name: str = '1.txt'):
    out = BytesIO()
    with tarfile.open(mode="w:xz", fileobj=out) as tar:
        if type(value) == str:
            data = value.encode('utf-8')
        else:
            data = value
        file = BytesIO(data)
        info = tarfile.TarInfo(name=file_name)
        info.size = len(data)
        tar.addfile(tarinfo=info, fileobj=file)
    return out.getvalue()


def unzip_raw(raw, file_name: str = '1.txt') -> bytes:
    with tempfile.TemporaryFile(mode='w+b') as f:
        f.write(raw)
        f.flush()
        f.seek(0)
        # noinspection PyTypeChecker
        with tarfile.open(fileobj=f, mode='r:xz') as tar:
            with tar.extractfile(file_name) as file:
                return file.read()
