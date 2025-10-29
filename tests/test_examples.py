from unittest.mock import MagicMock

import pytest
from pytest_examples import find_examples, CodeExample, EvalExample
from pytest_mock import MockerFixture


@pytest.mark.parametrize("example", find_examples("README.md", "doc/"), ids=str)
def test_examples(
    example: CodeExample,
    eval_example: EvalExample,
    mocker: MockerFixture,
):
    _ = mocker.patch("pathlib.Path.read_text", MagicMock(return_value=""))
    _ = eval_example.run_print_check(example)
