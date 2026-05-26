from pathlib import Path
from config.settings import SAFE_WORKSPACE


class WorkspaceState:
    def __init__(self):
        self.root = Path(SAFE_WORKSPACE).resolve()
        self.active_file = None
        self.open_files = []
        self.recent_commands = []
        self.current_directory = self.root

    def set_active_file(self, filepath: str):
        self.active_file = Path(filepath).resolve()
        if self.active_file not in self.open_files:
            self.open_files.append(self.active_file)

    def add_command(self, command: str):
        self.recent_commands.append(command)
        if len(self.recent_commands) > 20:
            self.recent_commands.pop(0)

    def is_within_workspace(self, path: Path) -> bool:
        try:
            resolved = path.resolve()
            return str(resolved).startswith(str(self.root))
        except (ValueError, OSError):
            return False

    def reset(self):
        self.active_file = None
        self.open_files.clear()
        self.recent_commands.clear()
        self.current_directory = self.root
