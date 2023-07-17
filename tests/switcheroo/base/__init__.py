from pathlib import Path
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description

class HasFileMode(BaseMatcher[Path]):
    """Hamcrest matcher to check the file mode of a given pathlib.Path
    """
    def __init__(self, file_mode: int) -> None:
        """Creates the matcher

        Args:
            file_mode (int): the file mode to check for - the check treats the int as a \
            octal value - ie if 755 is passed in, the matcher looks for the permission 0o755
        """
        super().__init__()
        self._file_mode = file_mode

    def _matches(self, item: Path) -> bool:
        file_mode_str = oct(item.stat().st_mode) #Returns 0o100[mode] as a str
        file_mode = int(file_mode_str[5:]) #Get just [mode]
        return file_mode == self._file_mode

    def describe_to(self, description: Description) -> None:
        description.append_text(f"File mode which is {self._file_mode} in octal") \
                   .append_text(f"(0o{self._file_mode})")
