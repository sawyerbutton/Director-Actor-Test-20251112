"""
Base Script Parser

Defines the abstract base class for all script parsers.
"""

from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from prompts.schemas import Script
import logging

logger = logging.getLogger(__name__)


class ScriptParser(ABC):
    """
    Abstract base class for script parsers.

    All format-specific parsers should inherit from this class and implement
    the parse() and validate() methods.
    """

    @abstractmethod
    def parse(self, file_path: str) -> Script:
        """
        Parse a script file and convert it to Script object.

        Args:
            file_path: Path to the script file

        Returns:
            Script object with scenes and metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        pass

    @abstractmethod
    def validate(self, script: Script) -> List[str]:
        """
        Validate the parsed script and return a list of warnings/errors.

        Args:
            script: Parsed Script object

        Returns:
            List of validation error/warning messages
        """
        pass

    def _read_file(self, file_path: str) -> str:
        """
        Read the content of a script file.

        Args:
            file_path: Path to the script file

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Script file not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"Read script file: {file_path} ({len(content)} chars)")
        return content

    def _validate_file_type(self, file_path: str, expected_extension: str):
        """
        Validate that the file has the expected extension.

        Args:
            file_path: Path to the file
            expected_extension: Expected file extension (e.g., '.txt')

        Raises:
            ValueError: If the file extension doesn't match
        """
        path = Path(file_path)

        if not path.suffix.lower() == expected_extension.lower():
            raise ValueError(
                f"Invalid file type. Expected {expected_extension}, "
                f"got {path.suffix}"
            )
