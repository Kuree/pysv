import enum


class DataType(enum.Enum):
    Bit = "bit"
    Byte = "byte"
    ShortInt = "shortint"
    Int = "int"
    LongInt = "longint"
    UByte = "byte unsigned"
    UShortInt = "shortint unsigned"
    UInt = "int unsigned"
    ULongInt = "longint unsigned"
    Object = "chandle"
    String = "string"
    # only for return type
    Void = "void"


class Reference:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
