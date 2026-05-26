from pathlib import Path
from security.sandbox import Sandbox
from security.permissions import Permissions

class FileGuard:
    def __init__(self, sandbox: Sandbox, permissions: Permissions):
        self.sandbox = sandbox
        self.permissions = permissions

    def can_access(self, path: str) -> bool:
        return self.sandbox.is_path_safe(path)

    def can_delete(self, path: str) -> bool:
        return self.can_access(path) and self.permissions.check("delete_file")
