import pytest
import os
import tempfile
import filecmp
import difflib


def get_tests_dir():
    return os.path.join(os.path.dirname(__file__), "tests")


def get_gold_dir():
    return os.path.join(get_tests_dir(), "gold")


def get_vectors_dir():
    return os.path.join(get_tests_dir(), "vectors")


def check_file_fn(src_str: str, vector_filename: str):
    vector_filename = os.path.join(get_gold_dir(), vector_filename)
    with tempfile.TemporaryDirectory() as temp:
        temp_filename = os.path.join(temp, "file")
        with open(temp_filename, "w+") as f:
            f.write(src_str)
        equal = filecmp.cmp(vector_filename, temp_filename)
        if not equal:
            with open(vector_filename) as f:
                vector_content = f.read()
            src_lines = src_str.splitlines()
            vector_lines = vector_content.splitlines()
            for line in difflib.unified_diff(vector_lines, src_lines,
                                             fromfile="gold_vector",
                                             tofile="test_output", lineterm=""):
                print(line)
        assert equal, "content are not equal"


@pytest.fixture
def check_file():
    return check_file_fn


def get_vector_filename_fn(filename):
    filename = os.path.join(get_vectors_dir(), filename)
    assert os.path.isfile(filename)
    return filename


@pytest.fixture
def get_vector_filename():
    return get_vector_filename_fn
