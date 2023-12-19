from enum import Enum

__all__ = ["Membership"]


class Membership(Enum):
    DEV = "Developer"
    OWN = "Owner"
    USR = "User"
