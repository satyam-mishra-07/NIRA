from pathlib import Path
from security.sandbox import Sandbox

class WorkspaceManager:
    def __init__(self, sandbox: Sandbox):
        self.sandbox = sandbox
        self.root = sandbox.workspace

    def list_files(self, subdir: str = "") -> list:
        target = self.root / subdir if subdir else self.root
        if not self.sandbox.is_path_safe(str(target)):
            return []
        if not target.exists():
            return []
        return [str(f.relative_to(self.root)) for f in target.iterdir() if f.is_file()]

    def read_file(self, path: str) -> str:
        target = self.sandbox.resolve_safe(path)
        if not target.exists():
            return ""
        return target.read_text(encoding="utf-8")
