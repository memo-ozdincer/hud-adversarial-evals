# server/scenarios/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseScenario(ABC):
    """
    An abstract base class for a self-contained evaluation scenario.

    This class defines the "contract" that every scenario module must follow.
    It ensures that the backend can interact with any scenario in a consistent way.
    """
    def __init__(self, session_user_id: str, session_user_role: str):
        self.session_user_id = session_user_id
        self.session_user_role = session_user_role
        self.state = self.get_initial_state()

    @abstractmethod
    def get_initial_state(self) -> Dict[str, Any]:
        """
        Returns the initial state dictionary for this specific scenario.
        This must be implemented by every subclass.
        """
        pass

    def read_file(self, path: str) -> str:
        """
        Default logic for reading a file from the scenario's virtual file system.
        This method enforces permission checks based on the session_user_role.
        """
        filesystem = self.state.get("filesystem", {})
        if path not in filesystem:
            raise ValueError(f"File not found: {path}")
        
        file_meta = filesystem[path]
        permissions = file_meta.get("permissions", [])
        
        if self.session_user_role not in permissions:
            raise PermissionError(f"Permission denied for role '{self.session_user_role}' to access {path}")
            
        return file_meta.get("content", "")

    def list_directory(self, path: str) -> List[str]:
        """Default logic for listing files. Simplified for our use case."""
        filesystem = self.state.get("filesystem", {})
        return list(filesystem.keys())