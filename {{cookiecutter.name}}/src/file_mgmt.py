import os


class FileManager:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def create_file(self, filename: str, content: str = "") -> str:
        path = os.path.join(self.base_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def read_file(self, filename: str) -> str:
        path = os.path.join(self.base_dir, filename)
        with open(path, "r") as f:
            return f.read()
