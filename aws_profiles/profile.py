from dataclasses import dataclass


@dataclass
class Profile:
    id_number: int
    access_key: str
    secret_access_key: str
    region: str
