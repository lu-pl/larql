"""Test utility for rdf-test syntax test discovery."""

from collections.abc import Iterator
from importlib.resources import files
from itertools import chain
from pathlib import Path
from string import Template
from typing import Literal as TypingLiteral
from urllib.parse import urlparse

from rdflib import Graph


class SPARQL11SyntaxTestDiscovery:
    def __init__(self, test_dir: Path | None = None):
        self.test_dir = Path("larql/tests/rdf-tests")
        self._manifest_all_file = (
            self.test_dir.joinpath("sparql/sparql11") / "manifest-all.ttl"
        )

    def _get_syntax_manifests(self) -> Iterator:
        manifest_all_graph: Graph = Graph().parse(self._manifest_all_file)

        query = """
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix mf: <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#>

        select distinct ?element
        where {
            ?collection rdf:rest*/rdf:first ?element .
            filter regex(str(?element), '/syntax-.+/manifest.ttl$')
        }
        """

        sparql_result = manifest_all_graph.query(query)
        yield from chain.from_iterable(sparql_result)  # type: ignore

    @staticmethod
    def _get_test_type(
        test_type: TypingLiteral["positive", "negative"],
    ) -> tuple[str, str]:
        match test_type:
            case "positive":
                return ("PositiveSyntaxTest11", "PositiveUpdateSyntaxTest11")
            case "negative":
                return ("NegativeSyntaxTest11", "NegativeUpdateSyntaxTest11")
            case _:
                raise Exception(
                    "Applicable values for parameter test_type are 'positive' or 'negative'."
                )

    def get_syntax_tests(self, test_type: TypingLiteral["positive", "negative"]):
        type_class_1, type_class_2 = self._get_test_type(test_type)
        _query_template = Template(
            """
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix mf: <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#>

            select ?action
            where {
                {?test a mf:$type_class_1.}
                union
                {?test a mf:$type_class_2.}

            ?test mf:action ?action .
            }
            """
        )

        query = _query_template.substitute(
            type_class_1=type_class_1, type_class_2=type_class_2
        )

        for manifest in self._get_syntax_manifests():
            graph = Graph().parse(manifest)
            sparql_result = graph.query(query)

            yield from map(
                lambda x: urlparse(x).path,
                chain.from_iterable(sparql_result),  # type: ignore
            )
