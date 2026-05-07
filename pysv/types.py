import enum


class ArrayType:
    def __init__(self, base_type, dim: int):
        self.base_type = base_type
        self.dim = dim

    def __eq__(self, other):
        return self.base_type == other


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
        assert dim > 0, "Array dim must be positive"
        return ArrayType(DataType.IntArray, dim)


class Reference:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
