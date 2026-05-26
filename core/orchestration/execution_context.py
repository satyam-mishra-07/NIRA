from pathlib import Path
from config.settings import (
    SAFE_MODE, ALLOW_TERMINAL_EXECUTION, ALLOW_BROWSER_AUTOMATION,
    ALLOWED_DIRECTORIES, SAFE_WORKSPACE,
)


class ExecutionContext:
    def __init__(self):
        self.safe_mode = SAFE_MODE
        self.terminal_allowed = ALLOW_TERMINAL_EXECUTION
        self.browser_allowed = ALLOW_BROWSER_AUTOMATION
        self.allowed_dirs = [Path(d).resolve() for d in ALLOWED_DIRECTORIES]
        self.workspace_root = Path(SAFE_WORKSPACE).resolve()

    def initialize(self):
        if not self.workspace_root.exists():
            self.workspace_root.mkdir(parents=True, exist_ok=True)

    def is_path_allowed(self, path: Path) -> bool:
        try:
            resolved = path.resolve()
            for allowed in self.allowed_dirs:
                if str(resolved).startswith(str(allowed)):
                    return True
            return str(resolved).startswith(str(self.workspace_root))
        except (ValueError, OSError):
            return False
