from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.discovery import SyntaxTestDiscovery, SyntaxTestInfo

W3C_SPARQL_TESTS = Path("./tests/rdf-tests/sparql")


def generate_params(
    marker: pytest.MarkDecorator, manifest: Path
) -> Iterator[pytest.mark.ParameterSet]:
    for test_info in SyntaxTestDiscovery(manifest):
        yield pytest.param(test_info, marks=marker, id=test_info.test_id)


@pytest.mark.parametrize(
    "test_info",
    [
        *generate_params(
            marker=pytest.mark.sparql10,
            manifest=W3C_SPARQL_TESTS / "sparql10/manifest.ttl",
        ),
        *generate_params(
            marker=pytest.mark.sparql11,
            manifest=W3C_SPARQL_TESTS / "sparql11/manifest-all.ttl",
        ),
        *generate_params(
            marker=pytest.mark.sparql12,
            manifest=W3C_SPARQL_TESTS / "sparql12/manifest.ttl",
        ),
    ],
)
def test_w3c_sparql_syntax_tests(test_info: SyntaxTestInfo):
    assert False
