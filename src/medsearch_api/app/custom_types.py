from enum import Enum


# etl
class OperationType(Enum):
    download = "download"
    create = "create"
    save = "save"
