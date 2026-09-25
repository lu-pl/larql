from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from urllib.parse import urlparse

from rdflib import Graph, URIRef
from sparqlx import SPARQLWrapper


@dataclass
class SyntaxTestInfo:
    test_id: URIRef
    test_path: Path
    valid: bool


class SyntaxTestDiscovery(Iterable[SyntaxTestInfo]):
    def __init__(self, manifest: Path) -> None:
        self._manifest = manifest

    def __iter__(self) -> Iterator[SyntaxTestInfo]:
        yield from self.entries

        for manifest in self.manifests:
            yield from SyntaxTestDiscovery(manifest=manifest)

    @cached_property
    def manifest_graph(self) -> Graph:
        return Graph().parse(source=self._manifest)

    @property
    def manifests(self) -> Iterator[Path]:
        manifest_discovery_query = """
        prefix mf: <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        
        select ?manifest
        where {
          [ mf:include/rdf:rest*/rdf:first ?manifest ] .
        }
        """
        wrapper = SPARQLWrapper(sparql_endpoint=self.manifest_graph)
        manifests: list[dict] = wrapper.query(manifest_discovery_query, convert=True)

        for manifest in manifests:
            path_uri: URIRef = manifest["manifest"]
            yield self._pathify_uri(path_uri=path_uri)

    @property
    def entries(self) -> Iterator[SyntaxTestInfo]:

        syntax_test_discovery_query = """
        prefix mf:  <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        select ?test_id ?test_path_uri ?valid
        where {
        values (?test_type ?validity) {
          (mf:PositiveSyntaxTest         true)
          (mf:PositiveUpdateSyntaxTest   true)
          (mf:PositiveSyntaxTest11       true)
          (mf:PositiveUpdateSyntaxTest11 true)

          (mf:NegativeSyntaxTest         false)
          (mf:NegativeUpdateSyntaxTest   false)
          (mf:NegativeSyntaxTest11       false)
          (mf:NegativeUpdateSyntaxTest11 false)
        }

        [ mf:entries/rdf:rest*/rdf:first ?test_id ] .

        ?test_id a ?test_type ;
          mf:action ?test_path_uri .
        }
        """

        wrapper = SPARQLWrapper(sparql_endpoint=self.manifest_graph)
        entries: list[dict] = wrapper.query(syntax_test_discovery_query, convert=True)

        for entry in entries:
            test_id: URIRef = entry["test_id"]
            test_path_uri: URIRef = entry["test_path_uri"]
            valid: bool = entry["valid"]

            test_path: Path = self._pathify_uri(path_uri=test_path_uri)

            yield SyntaxTestInfo(test_id=test_id, test_path=test_path, valid=valid)

    @staticmethod
    def _pathify_uri(path_uri: URIRef) -> Path:
        parsed = urlparse(path_uri)
        return Path(parsed.path)
