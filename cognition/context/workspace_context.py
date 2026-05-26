from pathlib import Path
from config.settings import SAFE_WORKSPACE

class WorkspaceContext:
    def __init__(self):
        self.root = Path(SAFE_WORKSPACE).resolve()
        self.file_snapshot = {}

    def scan(self) -> dict:
        if not self.root.exists():
            return {"files": [], "file_count": 0}
        files = [str(f.relative_to(self.root)) for f in self.root.rglob("*") if f.is_file()]
        self.file_snapshot = {f: True for f in files}
        return {"files": files[:50], "file_count": len(files)}

    def get_recent_files(self, count: int = 5) -> list:
        if not self.root.exists():
            return []
        files = sorted(self.root.rglob("*"), key=lambda f: f.stat().st_mtime if f.is_file() else 0, reverse=True)
        return [str(f.relative_to(self.root)) for f in files if f.is_file()][:count]
