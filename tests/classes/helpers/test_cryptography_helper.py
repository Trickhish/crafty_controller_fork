import pytest

from app.classes.helpers.cryptography_helper import CryptoHelper


def test_blake2_hash_bytes_known_value() -> None:
    """
    Test blake2_hash_bytes_known_value with known input and output values.

    Returns:

    """
    known_input: bytes = b"hello world"
    known_output: bytes = bytes.fromhex(
        "021ced8799296ceca557832ab941a50b4a11f83478cf141f51f933f653ab9fbcc05a037cddbed0"
        "6e309bf334942c4e58cdf1a46e237911ccd7fcf9787cbc7fd0"
    )
    assert CryptoHelper.blake2b_hash_bytes(known_input) == known_output


def test_bytes_to_b64_known_value() -> None:
    """
    Test bytes_to_b64 with known input and output values.

    Returns:

    """
    # Test 1
    known_value: bytes = b"hello world"
    known_output: str = "aGVsbG8gd29ybGQ="
    assert CryptoHelper.bytes_to_b64(known_value) == known_output

    # Test 2
    known_value_2: bytes = bytes.fromhex(
        "ca2b62821a7e069b7048508f1f2b6947cb7d1e196008da1d43cb7b0c1971ce78bfc5bb7d2cb37f"
        "c23cfaec56c870582ebf99237038405cec8b1626c20756e5dd"
    )
    known_output_2: str = (
        "yitighp+BptwSFCPHytpR8t9HhlgCNodQ8t7DBlxzni/xbt9LLN/wjz67FbIcFguv5kjcDhAXOyLFi"
        "bCB1bl3Q=="
    )
    assert CryptoHelper.bytes_to_b64(known_value_2) == known_output_2


def test_b64_to_bytes() -> None:
    known_input: bytes = bytes.fromhex(
        "69666a2bc393d582730e4db6974987707ba4c26211b78a174ab71b69bd446877"
    )
    known_output: str = "aWZqK8OT1YJzDk22l0mHcHukwmIRt4oXSrcbab1EaHc="
    assert CryptoHelper.bytes_to_b64(known_input) == known_output

    known_input_2: bytes = bytes.fromhex("1b5a3db0ca943f041a6010498bad753fa4e51893")
    known_output_2: str = "G1o9sMqUPwQaYBBJi611P6TlGJM="
    assert CryptoHelper.bytes_to_b64(known_input_2) == known_output_2


def test_bytes_to_hex_known_value() -> None:
    """
    Test bytes_to_hex with known input and output values.

    Returns:

    """
    # Test 1
    known_value_1: bytes = b"hello world"
    known_output_1: str = "68656c6c6f20776f726c64"
    assert CryptoHelper.bytes_to_hex(known_value_1) == known_output_1

    # Test 2
    known_value_2: bytes = b"boatisthebest"
    known_output_2: str = "626f6174697374686562657374"
    assert CryptoHelper.bytes_to_hex(known_value_2) == known_output_2


def test_str_to_b64() -> None:
    """

    Returns:

    """
    # Test 1
    known_value_1: str = "Hello World"
    known_output_1: str = "SGVsbG8gV29ybGQ="
    assert CryptoHelper.str_to_b64(known_value_1) == known_output_1

    known_value_2: str = "I love Crafty! Yee haw!"
    known_output_2: str = "SSBsb3ZlIENyYWZ0eSEgWWVlIGhhdyE="
    assert CryptoHelper.str_to_b64(known_value_2) == known_output_2


def test_b64_to_str() -> None:
    """
    Test known input with b64_to_str

    Returns:

    """
    # Test 1
    known_value_1: str = "SGVsbG8gV29ybGQ="
    known_output_1: str = "Hello World"
    assert CryptoHelper.b64_to_str(known_value_1) == known_output_1

    # Test 2
    known_value_2: str = "SSBsb3ZlIENyYWZ0eSEgWWVlIGhhdyE="
    known_output_2: str = "I love Crafty! Yee haw!"
    assert CryptoHelper.b64_to_str(known_value_2) == known_output_2


def test_b64_to_str_not_b64() -> None:
    """
    Test b64_to_str function when give a value that is not b64 encoded. Should return
    RuntimeError.

    Returns:

    """
    test_error_value: str = "!This is not B64 encoded text!"
    with pytest.raises(RuntimeError):
        _ = CryptoHelper.b64_to_str(test_error_value)


def test_b64_to_str_not_unicode() -> None:
    """
    Test b64_to_str with data that is not Unicode. Should return RuntimeError.

    Returns:

    """
    random_data: str = "gQ=="
    with pytest.raises(RuntimeError):
        _ = CryptoHelper.b64_to_str(random_data)
