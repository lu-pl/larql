"""Postive SPARQL 1.1 syntax parsing tests."""

from pathlib import Path

import pytest

from larql import SPARQLParser
from tests.discovery import SPARQL11SyntaxTestDiscovery


positive_test_paths = SPARQL11SyntaxTestDiscovery().get_syntax_tests("positive")


@pytest.mark.parametrize("test_query_path", positive_test_paths)
def test_positive_query_parsing(test_query_path):
    _query_file_path: Path = Path(test_query_path)
    query = _query_file_path.read_text()

    assert SPARQLParser(query)
