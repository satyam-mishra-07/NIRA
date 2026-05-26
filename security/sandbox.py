from pathlib import Path
from config.settings import SAFE_WORKSPACE, ALLOWED_DIRECTORIES

class Sandbox:
    def __init__(self):
        self.allowed = [Path(d).resolve() for d in ALLOWED_DIRECTORIES]
        self.workspace = Path(SAFE_WORKSPACE).resolve()

    def is_path_safe(self, path: str) -> bool:
        try:
            resolved = Path(path).resolve()
            for allowed in self.allowed:
                if str(resolved).startswith(str(allowed)):
                    return True
            return str(resolved).startswith(str(self.workspace))
        except (ValueError, OSError):
            return False

    def resolve_safe(self, path: str) -> Path:
        resolved = Path(path).resolve()
        if not self.is_path_safe(str(resolved)):
            raise PermissionError(f"Access denied: {path} is outside allowed directories")
        return resolved
