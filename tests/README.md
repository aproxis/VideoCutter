# Tests

This directory contains tests for the VideoCutter application. The tests are organized into unit tests that verify the functionality of individual components.

## Structure

```
tests/
├── __init__.py             # Package initialization
└── unit/                   # Unit tests
    ├── __init__.py         # Unit tests package initialization
    ├── test_config.py      # Tests for the config module
    ├── test_image.py       # Tests for the image module
    ├── test_utils.py       # Tests for the utils module
    └── test_video.py       # Tests for the video module
```

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=video_processing
```

To run a specific test file:

```bash
pytest tests/unit/test_config.py
```

To run a specific test:

```bash
pytest tests/unit/test_config.py::TestVideoConfig::test_default_values
```

## Test Configuration

The test configuration is defined in `pytest.ini` at the root of the project:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --cov=video_processing --cov-report=term-missing
```

This configuration:
- Looks for tests in the `tests` directory
- Considers files starting with `test_` as test files
- Considers functions starting with `test_` as test functions
- Runs tests verbosely with coverage reporting

## Writing Tests

When writing tests, follow these guidelines:

1. Use descriptive test names that explain what is being tested
2. Use the `unittest` framework with `pytest` for assertions
3. Use mocks and patches to isolate the code being tested
4. Test both success and failure cases
5. Test edge cases and boundary conditions

Example:

```python
import unittest
from unittest.mock import patch
from video_processing.config import VideoConfig

class TestVideoConfig(unittest.TestCase):
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = VideoConfig()
        self.assertEqual(config.segment_duration, 6)
        self.assertEqual(config.input_folder, 'INPUT')
        # ...
```

## Test Coverage

The test suite aims to achieve high coverage of the codebase. Coverage reports show which lines of code are executed during tests and which are not.

To view a detailed coverage report:

```bash
pytest --cov=video_processing --cov-report=html
```

This will generate an HTML report in the `htmlcov` directory that you can open in a web browser.
