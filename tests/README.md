# Test Harness Guide

## Writing Tests
- Stick to the Arrange → Act → Assert pattern and assert on external behavior.
- Test cases should be self explanitory and comments restricted to explain **why** things are done this way not **how**.
- Define commonly used variables at the class level for each testing module.
- Reuse helpers in `tests.tools` and `tests.random_data_library` for brevity.

## Running Tests
- Full suite: `uv run pytest tests`.
- Single module: `uv run pytests tests/test_shop.py`.

## Warnings
- WARNING: Tests may change your game configuration (as an example, your saves could be deleted !).
- WARNING: The game must be set to English before running tests. Other languages will cause test case failure.
