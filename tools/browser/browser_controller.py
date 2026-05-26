from security.permissions import Permissions

class BrowserController:
    def __init__(self, permissions: Permissions):
        self.permissions = permissions
        self.enabled = permissions.browser_allowed

    def search(self, query: str) -> list:
        if not self.enabled:
            return []
        return [{"title": "Search stub", "url": f"https://example.com/search?q={query}"}]
