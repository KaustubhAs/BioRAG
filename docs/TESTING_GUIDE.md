# 🧪 Testing Guide for Biomedical Assistant

This guide provides comprehensive information about testing the Biomedical Assistant project using pytest.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Coverage Reports](#coverage-reports)
6. [Writing Tests](#writing-tests)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Install test dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest --version
```

### Run All Tests
```bash
# Using the test runner (recommended)
python run_tests.py

# Using pytest directly
python -m pytest tests/ -v
```

## 🏗️ Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_knowledge_graph.py  # Knowledge graph component tests
├── test_rag_system.py       # RAG system tests
├── test_app_components.py   # Application component tests
├── test_performance.py      # Performance and stress tests
├── test_edge_cases.py       # Edge case and error handling tests
├── test_system.py           # Legacy system tests
└── test_search_neighborhood.py # Legacy search tests
```

### Key Components

- **`conftest.py`**: Central configuration with shared fixtures
- **Test files**: Organized by component/module
- **Fixtures**: Reusable test data and objects
- **Markers**: Test categorization and filtering

## 🏃‍♂️ Running Tests

### Using the Test Runner (Recommended)

```bash
# Run all tests with coverage
python run_tests.py

# Run only unit tests
python run_tests.py --type unit

# Run performance tests only
python run_tests.py --type performance

# Run tests without coverage
python run_tests.py --no-coverage

# Run specific test file
python run_tests.py --file tests/test_knowledge_graph.py

# Generate coverage report only
python run_tests.py --coverage-only
```

### Using pytest Directly

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_knowledge_graph.py -v

# Run tests with specific marker
python -m pytest tests/ -m unit -v

# Run tests excluding slow tests
python -m pytest tests/ -m "not slow" -v

# Run tests with coverage
python -m pytest tests/ --cov=knowledge_graph --cov=rag --cov=app -v
```

### Test Selection Options

```bash
# Run by test type
python run_tests.py --type unit      # Unit tests only
python run_tests.py --type integration # Integration tests only
python run_tests.py --type performance # Performance tests only
python run_tests.py --type stress     # Stress tests only
python run_tests.py --type fast       # Fast tests (exclude slow)

# Run by component
python -m pytest tests/test_knowledge_graph.py  # Knowledge graph tests
python -m pytest tests/test_rag_system.py      # RAG system tests
python -m pytest tests/test_app_components.py  # App component tests
```

## 🏷️ Test Categories

### Unit Tests (`@pytest.mark.unit`)
- **Purpose**: Test individual functions and methods in isolation
- **Scope**: Single component or function
- **Speed**: Fast execution (< 100ms per test)
- **Dependencies**: Minimal, mostly mocked

**Example**:
```python
@pytest.mark.unit
def test_data_processor_initialization(self, sample_data):
    """Test data processor initialization."""
    processor = DataProcessor(sample_data)
    assert processor.data == sample_data
```

### Integration Tests (`@pytest.mark.integration`)
- **Purpose**: Test component interactions and data flow
- **Scope**: Multiple components working together
- **Speed**: Medium execution (100ms - 1s per test)
- **Dependencies**: Real data processing, minimal mocking

**Example**:
```python
@pytest.mark.integration
def test_end_to_end_pipeline(self, mock_dataset_path):
    """Test complete pipeline from data to graph."""
    diseases, symptoms, relationships = preprocess_data(mock_dataset_path)
    graph = build_graph(diseases, symptoms, relationships)
    assert len(graph.nodes) > 0
```

### Performance Tests (`@pytest.mark.performance`)
- **Purpose**: Test system performance and efficiency
- **Scope**: System-wide performance metrics
- **Speed**: Variable execution (1s - 10s per test)
- **Dependencies**: Real system components, timing measurements

**Example**:
```python
@pytest.mark.performance
def test_query_processing_performance(self, sample_graph):
    """Test query processing performance."""
    start_time = time.time()
    response = rag_system.answer_query("Test query")
    query_time = time.time() - start_time
    assert query_time < 2.0  # Should complete within 2 seconds
```

### Stress Tests (`@pytest.mark.stress`)
- **Purpose**: Test system behavior under load and stress
- **Scope**: System-wide stress scenarios
- **Speed**: Slow execution (10s+ per test)
- **Dependencies**: Real system, concurrent operations

**Example**:
```python
@pytest.mark.stress
def test_large_number_of_queries(self, sample_graph):
    """Test system with large number of queries."""
    for i in range(100):
        response = rag_system.answer_query(f"Query {i}")
        assert isinstance(response, str)
```

### Slow Tests (`@pytest.mark.slow`)
- **Purpose**: Mark tests that take longer to execute
- **Scope**: Any test category that's slow
- **Speed**: > 5 seconds per test
- **Usage**: Can be excluded with `-m "not slow"`

## 📊 Coverage Reports

### HTML Coverage Report
```bash
# Generate HTML coverage report
python run_tests.py --type all

# View in browser
# Open htmlcov/index.html
```

### Terminal Coverage Report
```bash
# View coverage in terminal
python -m coverage report

# View detailed coverage
python -m coverage report --show-missing
```

### Coverage Targets
- **Minimum Coverage**: 80% (set in pytest.ini)
- **Target Coverage**: 90%+
- **Coverage Areas**: knowledge_graph, rag, app modules

## ✍️ Writing Tests

### Test File Structure
```python
"""
Tests for [Component Name]
"""
import pytest
from unittest.mock import Mock, patch

from [module] import [Class/Function]

class Test[ClassName]:
    """Test [Class/Function] functionality."""
    
    @pytest.mark.unit
    def test_[functionality_name](self, [fixtures]):
        """Test [specific functionality]."""
        # Arrange
        input_data = "test input"
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == "expected output"
```

### Using Fixtures
```python
def test_with_fixtures(self, sample_graph, mock_llm):
    """Test using multiple fixtures."""
    rag_system = BiomedicalRAG(sample_graph)
    rag_system.llm = mock_llm
    
    response = rag_system.answer_query("Test query")
    assert isinstance(response, str)
```

### Mocking External Dependencies
```python
@patch('rag.response_generator.Ollama')
def test_with_mocked_ollama(self, mock_ollama):
    """Test with mocked Ollama."""
    mock_llm = Mock()
    mock_llm.return_value = "Mocked response"
    mock_ollama.return_value = mock_llm
    
    # Test implementation
    pass
```

### Testing Edge Cases
```python
def test_edge_case_empty_input(self):
    """Test handling of empty input."""
    with pytest.raises(ValueError):
        process_data("")
    
def test_edge_case_none_input(self):
    """Test handling of None input."""
    with pytest.raises(TypeError):
        process_data(None)
```

## 🎯 Best Practices

### Test Organization
1. **Group related tests** in test classes
2. **Use descriptive test names** that explain the scenario
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Keep tests independent** - no test should depend on another

### Test Data Management
1. **Use fixtures** for reusable test data
2. **Create minimal test data** that covers the test case
3. **Use temporary files** for file-based tests
4. **Clean up resources** after tests

### Assertions
1. **Use specific assertions** rather than generic ones
2. **Test one thing per test** method
3. **Include meaningful error messages** in assertions
4. **Test both positive and negative cases**

### Performance Considerations
1. **Mock slow operations** in unit tests
2. **Use appropriate test markers** for slow tests
3. **Set reasonable timeouts** for performance tests
4. **Measure actual performance** not just pass/fail

## 🔧 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure you're in the project root directory
cd /path/to/BiomedicalAssistant

# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Missing Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Install test dependencies specifically
pip install pytest pytest-cov pytest-mock
```

#### Test Discovery Issues
```bash
# Check test file naming
# Files should start with "test_"
# Test functions should start with "test_"

# Run with explicit path
python -m pytest tests/test_knowledge_graph.py -v
```

#### Coverage Issues
```bash
# Check if coverage is properly configured
python -m pytest --cov=knowledge_graph --cov-report=term-missing

# Generate coverage from scratch
python -m coverage run -m pytest tests/
python -m coverage report
```

### Debugging Tests

#### Verbose Output
```bash
# Increase verbosity
python -m pytest tests/ -v -s

# Show local variables on failure
python -m pytest tests/ -v -s --tb=long
```

#### Running Single Test
```bash
# Run specific test method
python -m pytest tests/test_knowledge_graph.py::TestDataProcessor::test_preprocess_data_success -v

# Run tests matching pattern
python -m pytest tests/ -k "test_preprocess" -v
```

#### Interactive Debugging
```python
def test_debug_example(self):
    """Example of debugging a test."""
    import pdb; pdb.set_trace()  # Add breakpoint
    result = function_to_test()
    assert result == expected_value
```

## 📈 Test Metrics

### Coverage Goals
- **Overall Coverage**: 90%+
- **Critical Modules**: 95%+
- **New Features**: 100%

### Performance Benchmarks
- **Unit Tests**: < 100ms per test
- **Integration Tests**: < 1s per test
- **Performance Tests**: < 5s per test
- **Stress Tests**: < 60s per test

### Quality Metrics
- **Test Count**: 50+ tests
- **Test Categories**: All major components covered
- **Edge Cases**: Comprehensive error handling
- **Documentation**: All tests documented

## 🚀 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python run_tests.py --type all
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

---

**Happy Testing! 🧪✨**
