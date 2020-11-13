import enum


class DataType(enum.Enum):
    Bit = 1
    ShortInt = 16
    Int = 32
    LongInt = 64
    UShortInt = 16
    UInt = 32
    ULongInt = 64
    # only for return type
    Void = 0
