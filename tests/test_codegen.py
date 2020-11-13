from pysv import get_dpi_definition, dpi, DataType


def test_get_dpi_definition():
    @dpi(a=DataType.String, b=DataType.Byte, return_type=DataType.CHandle)
    def func(a, b):
        return a + b

    result = get_dpi_definition(func)
    expected = 'import "DPI-C" function chandle func(input string a,\n' \
               '                                     input byte b);'
    assert result == expected

    result = get_dpi_definition(func, pretty_print=False)
    expected = 'import "DPI-C" function chandle func(input string a, input byte b);' # noqa
    assert expected == result


if __name__ == "__main__":
    test_get_dpi_definition()
