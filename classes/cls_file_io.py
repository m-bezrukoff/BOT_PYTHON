import pickle
from os import path, remove
# import zstd
import zstandard as zstd


class FileIO:
    def save_file(self, _path, data):
        with open(_path, 'ab') as f:
            f.write((data + '\r\n').encode('UTF-8'))

    def save_file_multiline(self, _path, _list):
        with open(_path, 'a', encoding="utf-8") as f:
            f.writelines(map(lambda x: x + '\n', _list))

    def load_file(self, _path):
        if path.isfile(_path) and path.getsize(_path) > 0:
            with open(_path, 'rb') as f:
                return f.read()
        else:
            return None

    def delete_file(self, _path):
        remove(_path)

    def save_zipped_file(self, _path, data):
        with open(_path, 'wb') as f:
            f.write(zstd.compress(pickle.dumps(data, protocol=-1), 1))

    def load_zipped_file(self, _path):
        if path.isfile(_path) and path.getsize(_path) > 0:
            with open(_path, 'rb') as f:
                # return pickle.loads(z_std.decode(f.read()))
                return pickle.loads(zstd.decompress(f.read()))
        else:
            raise FileNotFoundError(_path)
