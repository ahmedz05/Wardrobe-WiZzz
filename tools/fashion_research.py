"""Read-only, offline integrity checks and lexical retrieval for research snapshots.

No backend, network, database, model or credential dependencies. Validation never
establishes truth, brand identity, expert approval or permission to train models.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date
import hashlib
from ipaddress import ip_address
import json
import math
from pathlib import Path
import re
import sys
from typing import Any
import unicodedata
from urllib.parse import urlsplit, urlunsplit

DEEP_FILE = "wardrobe_wizzz_fashion_intelligence_deep_research.json"
REGISTRY_FILE = "wardrobe_wizzz_global_brand_discovery_registry.json"
DEFAULT_DIRECTORY = Path(__file__).resolve().parents[1] / "wardrobe_wizzz_fashion_research_bundle/research"
MAX_FILE_BYTES = 16 * 1024 * 1024
KINDS = ("observation", "candidate", "comparison", "fusion", "scenario")


class ResearchError(ValueError):
    """Input cannot safely be interpreted or queried."""


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    location: str
    message: str


@dataclass(frozen=True)
class Source:
    key: str
    title: str
    url: str
    source_type: str
    declared_rights: str
    publisher: str | None


@dataclass(frozen=True)
class Entry:
    key: str
    kind: str
    location: str
    title: str
    data: dict[str, Any]
    source_keys: tuple[str, ...]
    related_records: tuple[str, ...]
    declared_status: str


def _words(value: str) -> set[str]:
    folded = "".join(c for c in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(c))
    return set(re.findall(r"[^\W_]+", folded, re.UNICODE))


def _identity(value: str) -> str:
    # Unlike search, identity comparison retains diacritics. Collisions are review
    # candidates only: punctuation can distinguish two real businesses.
    return "".join(c for c in unicodedata.normalize("NFKC", value).casefold() if c.isalnum())


def _url(value: str) -> str:
    parts = urlsplit(value)
    host = (parts.hostname or "").lower().rstrip(".")
    if (parts.scheme not in {"http", "https"} or not host or parts.username is not None
            or parts.password is not None or any(c.isspace() for c in value)
            or host == "localhost" or host.endswith((".localhost", ".local"))):
        raise ValueError("Not an eligible public reference URL")
    _ = parts.port  # Reject malformed/out-of-range ports without contacting DNS.
    try:
        address = ip_address(host)
    except ValueError:
        if "." not in host:
            raise ValueError("A public hostname is required") from None
    else:
        if not address.is_global:
            raise ValueError("Nonpublic address")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, ""))


def _read(path: Path) -> tuple[dict[str, Any], str]:
    def unique(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ResearchError("Duplicate JSON object key; input was not silently overwritten")
            result[key] = value
        return result

    def reject_constant(_: str) -> None:
        raise ResearchError("Non-finite JSON number")

    def finite_float(value: str) -> float:
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ResearchError("Unrepresentable JSON number")
        return parsed

    try:
        with path.open("rb") as stream:
            payload = stream.read(MAX_FILE_BYTES + 1)
        if len(payload) > MAX_FILE_BYTES:
            raise ResearchError(f"{path.name}: exceeds the {MAX_FILE_BYTES}-byte input limit")
        data = json.loads(payload.decode("utf-8-sig"), object_pairs_hook=unique,
                          parse_constant=reject_constant, parse_float=finite_float)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ResearchError(f"{path.name}: unreadable UTF-8 JSON ({type(exc).__name__})") from None
    if not isinstance(data, dict):
        raise ResearchError(f"{path.name}: root must be an object")
    return data, hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class Corpus:
    datasets: dict[str, dict[str, Any]]
    sources: dict[str, Source]
    entries: tuple[Entry, ...]
    findings: tuple[Finding, ...]

    def report(self) -> dict[str, Any]:
        counts = dict(Counter(entry.kind for entry in self.entries))
        counts.update(entries=len(self.entries), sources=len(self.sources), verified_brands=0, training_cleared=0)
        return {"report_version": 1, "verification_scope": "offline_integrity_only",
                "fact_verification_performed": False, "datasets": deepcopy(self.datasets), "counts": counts,
                "errors": sum(f.severity == "error" for f in self.findings),
                "warnings": sum(f.severity == "warning" for f in self.findings),
                "finding_counts": dict(sorted(Counter(f.code for f in self.findings).items())),
                "findings": [asdict(f) for f in self.findings]}

    def search(self, text: str = "", *, kind: str | None = None, area: str | None = None,
               status: str | None = None, source: str | None = None, limit: int = 20) -> dict[str, Any]:
        if any(f.severity == "error" for f in self.findings):
            raise ResearchError("Integrity errors must be resolved before querying this snapshot")
        if type(limit) is not int or not 1 <= limit <= 100 or len(text) > 500:
            raise ValueError("Use limit 1..100 and a query of at most 500 characters")
        if kind is not None and kind not in KINDS:
            raise ValueError("Unknown entry kind")
        if source is not None and source not in self.sources:
            raise ValueError("Unknown namespaced source")
        terms = _words(text)
        matches: list[tuple[int, Entry]] = []
        for entry in self.entries:
            if ((kind is not None and entry.kind != kind)
                    or (area is not None and entry.data.get("concept_area") != area)
                    or (status is not None and entry.declared_status != status)
                    or (source is not None and source not in entry.source_keys)):
                continue
            if terms <= _words(json.dumps(entry.data, ensure_ascii=False)):
                matches.append((len(terms & _words(entry.title)), entry))
        matches.sort(key=lambda row: (-row[0], row[1].key))
        results = []
        for _, entry in matches[:limit]:
            sources = [asdict(self.sources[key]) for key in entry.source_keys]
            caveats = ["retrieval_is_not_fact_verification"]
            if any(item["source_type"].startswith("house_") for item in sources):
                caveats.append("publisher_self_description")
            if entry.kind in {"comparison", "fusion"}:
                caveats.append("design_hypothesis_not_styling_rule")
            if entry.kind == "scenario":
                caveats.append("proposed_benchmark_not_executed")
            if entry.kind == "observation":
                caveats.append("engine_implication_is_a_proposal")
            if entry.kind == "candidate":
                caveats.append("brand_or_designer_identity_unresolved")
            results.append({"key": entry.key, "kind": entry.kind, "location": entry.location,
                            "data": deepcopy(entry.data), "declared_status": entry.declared_status,
                            "verification": "not_independently_verified", "training_use": "not_cleared",
                            "sources": sources, "related_records": list(entry.related_records), "caveats": caveats})
        return {"retrieval": "lexical_all_terms", "matched": len(matches), "results": results,
                "verification_scope": "offline_integrity_only"}


class _Builder:
    def __init__(self, as_of: date) -> None:
        self.as_of = as_of
        self.sources: dict[str, Source] = {}
        self.entries: list[Entry] = []
        self.findings: list[Finding] = []

    def issue(self, code: str, location: str, message: str, severity: str = "error") -> None:
        self.findings.append(Finding(severity, code, location, message))

    def text_fields(self, item: dict[str, Any], fields: tuple[str, ...], location: str) -> bool:
        bad = [key for key in fields if not isinstance(item.get(key), str) or not item[key].strip()]
        for key in bad:
            self.issue("invalid_field", location + "/" + key, "Expected a nonempty string")
        return not bad

    def strings(self, value: Any, location: str, required: bool = False) -> tuple[str, ...]:
        if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value) or (required and not value):
            self.issue("invalid_field", location, "Expected a list of nonempty strings")
            return ()
        if len(value) != len(set(value)):
            self.issue("duplicate_reference", location, "Repeated reference/alias retained in input", "warning")
        return tuple(dict.fromkeys(value))

    def check_date(self, value: Any, location: str) -> None:
        try:
            if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError
            parsed = date.fromisoformat(value)
        except ValueError:
            self.issue("invalid_date", location, "Expected an ISO YYYY-MM-DD date")
        else:
            if parsed > self.as_of:
                self.issue("future_date", location, "Recorded date is after the validation date", "warning")

    def add_source(self, namespace: str, identifier: Any, item: Any, location: str) -> None:
        if not isinstance(identifier, str) or not identifier.strip() or not isinstance(item, dict):
            self.issue("invalid_field", location, "Source requires a string ID and object")
            return
        type_field, rights_field = ("source_type", "rights_status") if namespace == "deep" else ("type", "license")
        required = ("title", "url", type_field, rights_field)
        if namespace == "deep" or "publisher" in item:
            required += ("publisher",)
        if not self.text_fields(item, required, location):
            return
        key = namespace + ":" + identifier
        if key in self.sources:
            self.issue("duplicate_id", location, "Source ID is repeated within its dataset")
            return
        try:
            _url(item["url"])
        except ValueError:
            self.issue("invalid_source_url", location + "/url", "Malformed, credential-bearing or nonpublic URL; never fetched")
        self.sources[key] = Source(key, item["title"], item["url"], item[type_field], item[rights_field], item.get("publisher"))
        if not item.get("access_date") or not item.get("publication_date"):
            self.issue("source_dates_missing", location, "Per-source access/publication dates are incomplete", "warning")
        for field in ("access_date", "publication_date"):
            if item.get(field):
                self.check_date(item[field], location + "/" + field)

    def add_entries(self, namespace: str, section: str, kind: str, items: list[Any]) -> None:
        required = {
            "observation": ("id", "kind", "observation", "concept_area", "concept_key", "critical_counterpoint", "proposed_engine_implication", "review_status", "confidence_in_factual_claim"),
            "candidate": ("name", "research_status", "entity_type"),
            "comparison": ("id", "tension", "pole_a", "pole_b", "design_consequence", "status"),
            "fusion": ("id", "fusion", "research_question", "counterargument", "status"),
            "scenario": ("id", "name", "given", "expectation"),
        }[kind]
        seen: set[str] = set()
        for index, item in enumerate(items):
            location = f"{namespace}:/{section}/{index}"
            if not isinstance(item, dict):
                self.issue("invalid_field", location, "Expected an object")
                continue
            if not self.text_fields(item, required, location):
                continue
            identifier = str(index) if kind == "candidate" else item["id"]
            if identifier in seen:
                self.issue("duplicate_id", location, "Record ID is repeated within its section")
                continue
            seen.add(identifier)
            title = item[{"observation": "observation", "candidate": "name", "comparison": "tension", "fusion": "fusion", "scenario": "name"}[kind]]
            ref_field = "sources" if kind == "comparison" else "source_ids"
            refs = self.strings(item.get(ref_field, []), location + "/" + ref_field, kind in {"observation", "candidate", "comparison"})
            source_keys = tuple(namespace + ":" + reference for reference in refs)
            for key in source_keys:
                if key not in self.sources:
                    self.issue("unknown_source", location, "Unresolved source reference: " + key)
            related = self.strings(item.get("supporting_records", []), location + "/supporting_records") if kind == "scenario" else ()
            if kind == "candidate":
                self.strings(item.get("aliases", []), location + "/aliases")
                self.strings(item.get("verification_needed", []), location + "/verification_needed")
                self.issue("discovery_only", location, "Directory discovery does not establish a brand identity", "warning")
            elif kind == "observation":
                self.issue("review_required", location, "Source-linked observation is not independently verified", "warning")
                if not item.get("era") or not item.get("geography"):
                    self.issue("context_missing", location, "Era/geography context is incomplete", "warning")
            elif kind == "fusion":
                self.strings(item.get("components", []), location + "/components", True)
                if not refs:
                    self.issue("hypothesis_needs_evidence", location, "Fusion remains an unsupported design question", "warning")
            elif kind == "scenario" and not related:
                self.issue("scenario_without_supporting_records", location, "Proposed evaluation lacks linked observations", "warning")
            status = item.get("review_status", item.get("research_status", item.get("status", "proposed_not_executed")))
            self.entries.append(Entry(f"{namespace}:{kind}:{identifier}", kind, location, title, item, source_keys,
                                      tuple("deep:observation:" + reference for reference in related), status))

    def cross_checks(self) -> None:
        keys = {entry.key for entry in self.entries}
        names: dict[str, set[str]] = defaultdict(set)
        urls: dict[str, list[str]] = defaultdict(list)
        for entry in self.entries:
            for reference in entry.related_records:
                if reference not in keys:
                    self.issue("unknown_record", entry.location, "Unresolved supporting observation: " + reference)
            if entry.kind == "candidate":
                aliases = entry.data.get("aliases", [])
                for name in [entry.title, *(aliases if isinstance(aliases, list) else [])]:
                    if isinstance(name, str) and _identity(name):
                        names[_identity(name)].add(entry.key)
        for key, identities in sorted(names.items()):
            if len(identities) > 1:
                self.issue("identity_collision", "registry:/candidates", key + ": " + ", ".join(sorted(identities)) + "; review, never auto-merge", "warning")
        for source in self.sources.values():
            try:
                urls[_url(source.url)].append(source.key)
            except ValueError:
                continue
        for identities in urls.values():
            if len(identities) > 1:
                self.issue("duplicate_source_url", "sources", ", ".join(identities) + "; not independent evidence", "warning")


def load_corpus(directory: Path, *, as_of: date | None = None) -> Corpus:
    """Load the two current formats without changing files or contacting services."""
    builder = _Builder(as_of or date.today())
    metadata: dict[str, dict[str, Any]] = {}
    documents: dict[str, dict[str, Any]] = {}
    sections = (("research_records", "observation"), ("counterexample_tests", "scenario"),
                ("dialectical_comparisons", "comparison"), ("fusion_studies", "fusion"))
    for namespace, filename in (("deep", DEEP_FILE), ("registry", REGISTRY_FILE)):
        data, digest = _read(Path(directory) / filename)
        documents[namespace] = data
        builder.text_fields(data, ("version",), namespace + ":/")
        date_field = "research_date" if namespace == "deep" else "as_of"
        builder.check_date(data.get(date_field), namespace + ":/" + date_field)
        metadata[namespace] = {"file": filename, "sha256": digest, "declared_version": data.get("version"), "declared_date": data.get(date_field)}
        sources = data.get("sources")
        if namespace == "deep":
            if not isinstance(sources, list):
                raise ResearchError("deep.sources must be a list")
            for index, item in enumerate(sources):
                builder.add_source(namespace, item.get("source_id") if isinstance(item, dict) else None, item, f"deep:/sources/{index}")
        else:
            if not isinstance(sources, dict):
                raise ResearchError("registry.sources must be an object")
            for identifier, item in sources.items():
                builder.add_source(namespace, identifier, item, "registry:/sources/" + identifier)
        for section, kind in (sections if namespace == "deep" else (("candidates", "candidate"),)):
            items = data.get(section, [] if section != "research_records" and section != "candidates" else None)
            if not isinstance(items, list):
                raise ResearchError(namespace + "." + section + " must be a list")
            builder.add_entries(namespace, section, kind, items)
    deep, registry = documents["deep"], documents["registry"]
    statistics = deep.get("statistics", {})
    if not isinstance(statistics, dict):
        raise ResearchError("deep.statistics must be an object")
    expected = {"source_count": len(deep["sources"]), "research_observation_count": len(deep["research_records"]),
                "evaluation_scenarios": len(deep.get("counterexample_tests", [])),
                "dialectical_comparisons": len(deep.get("dialectical_comparisons", [])), "fusion_hypotheses": len(deep.get("fusion_studies", []))}
    for field, count in expected.items():
        if field in statistics and (type(statistics[field]) is not int or statistics[field] != count):
            builder.issue("count_mismatch", "deep:/statistics/" + field, "Declared count differs from actual list size")
    for field, count in (("current_directory_candidate_count", len(registry["candidates"])),
                         ("raw_source_entry_count", sum(len(e.source_keys) for e in builder.entries if e.kind == "candidate"))):
        if type(registry.get(field)) is not int or registry[field] != count:
            builder.issue("count_mismatch", "registry:/" + field, "Declared count differs from indexed source mentions/candidates")
    builder.cross_checks()
    return Corpus(metadata, builder.sources, tuple(builder.entries), tuple(builder.findings))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-dir", type=Path, default=DEFAULT_DIRECTORY)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Check integrity; warnings are not fact verification")
    validate.add_argument("--strict", action="store_true", help="Return 1 for quality warnings as well as errors")
    query = commands.add_parser("query", help="Search all query terms with provenance; no inference")
    query.add_argument("text", nargs="?", default="")
    query.add_argument("--kind", choices=KINDS)
    query.add_argument("--area")
    query.add_argument("--status")
    query.add_argument("--source", help="Namespaced source, e.g. deep:S02 or registry:fhcm_paris")
    query.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        corpus = load_corpus(args.research_dir)
        if args.command == "validate":
            result = corpus.report()
            code = int(result["errors"] > 0 or (args.strict and result["warnings"] > 0))
        else:
            result = corpus.search(args.text, kind=args.kind, area=args.area, status=args.status, source=args.source, limit=args.limit)
            result["datasets"] = deepcopy(corpus.datasets)
            code = 0
    except (ResearchError, ValueError) as exc:
        result, code = {"error": str(exc), "verification_scope": "offline_integrity_only"}, 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
