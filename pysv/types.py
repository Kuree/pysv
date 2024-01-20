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

    def __new__(cls, *args, **kargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _):
        self.dim = 1

    def __getitem__(self, dim: int):
        assert self == DataType.IntArray, "Only Int array allowed to have dimensions"
        assert isinstance(dim, int), "Array dim must be an integer"
        res = DataType.IntArray
        res.dim = dim
        return res


class Reference:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
