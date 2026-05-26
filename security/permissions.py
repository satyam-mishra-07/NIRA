from config.settings import SAFE_MODE, CONFIRM_FILE_DELETE, ALLOW_TERMINAL_EXECUTION, ALLOW_BROWSER_AUTOMATION

class Permissions:
    def __init__(self):
        self.safe_mode = SAFE_MODE
        self.confirm_delete = CONFIRM_FILE_DELETE
        self.terminal_allowed = ALLOW_TERMINAL_EXECUTION
        self.browser_allowed = ALLOW_BROWSER_AUTOMATION

    def check(self, action: str) -> bool:
        checks = {
            "delete_file": self.confirm_delete,
            "terminal_exec": self.terminal_allowed,
            "browser_auto": self.browser_allowed,
            "file_write": not self.safe_mode or True,
        }
        return checks.get(action, False)

    def require_confirm(self, action: str) -> bool:
        return action in ("delete_file", "terminal_exec")
