import enum


class DataType(enum.Enum):
    Bit = enum.auto()
    Byte = enum.auto()
    ShortInt = enum.auto()
    Int = enum.auto()
    LongInt = enum.auto()
    UByte = enum.auto()
    UShortInt = enum.auto()
    UInt = enum.auto()
    ULongInt = enum.auto()
    Object = enum.auto()
    String = enum.auto()
    Float = enum.auto()
    Double = enum.auto()
    # only for return type
    Void = enum.auto()
    # the only array type supported
    IntArray = enum.auto()


class Reference:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
