from security.permissions import Permissions
from security.validator import InputValidator

class TerminalController:
    def __init__(self, permissions: Permissions, validator: InputValidator):
        self.permissions = permissions
        self.validator = validator
        self.allowed = permissions.terminal_allowed

    def execute(self, command: str) -> dict:
        if not self.allowed:
            return {"success": False, "output": "Terminal execution disabled by configuration"}
        validation = self.validator.validate_message(command)
        if not validation["safe"]:
            return {"success": False, "output": f"Command rejected: {validation['reason']}"}
        return {"success": True, "output": f"Would execute: {command}"}
