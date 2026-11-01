#!/usr/bin/env python3
"""Send traces and eval scores to the stack's Phoenix project through Octo (#64).

Octo forwards OpenTelemetry traces (OTLP over HTTP, protobuf) unchanged to
Phoenix, the trace viewer it runs next to itself, under the project of the
key's workspace. The stack's scripts use only the standard library, so this
module encodes the few protobuf messages a trace needs by hand rather than
depending on the OpenTelemetry SDK.

Spans carry metadata only: names, paths, sizes, hashes, timings and short
model answers. Never put a secret or a file's contents in one.

    from otlp import Phoenix, Span
    phoenix = Phoenix(key)              # None-safe: Phoenix.from_env() returns None without a key
    root = Span("sync", {"files": 77})
    child = root.child("ingest", {"path": "pcm/PROJECT.md"})
    child.end(); root.end()
    phoenix.send([root, child])
    phoenix.annotate(child, "verdict", label="pass", score=1.0)
"""
from __future__ import annotations

import json
import os
import secrets
import struct
import time
import urllib.parse
import urllib.request
from typing import Any

BASE = os.environ.get("OCTO_URL", "https://octodb.design-bakery.com/api")
KEY_ENV = "OCTO_STACK_WS_KEY"


# --- protobuf wire format: just the parts OTLP traces use -------------------

def _varint(n: int) -> bytes:
    n &= (1 << 64) - 1  # negative int64 values are sent as ten-byte two's complement
    out = bytearray()
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _field(number: int, wire: int, payload: bytes) -> bytes:
    return _varint(number << 3 | wire) + payload


def _bytes(number: int, data: bytes) -> bytes:
    return _field(number, 2, _varint(len(data)) + data)


def _str(number: int, text: str) -> bytes:
    return _bytes(number, text.encode("utf-8"))


def _fixed64(number: int, n: int) -> bytes:
    return _field(number, 1, struct.pack("<Q", n))


def _any_value(value: Any) -> bytes:
    if isinstance(value, bool):
        return _field(2, 0, _varint(int(value)))
    if isinstance(value, int):
        return _field(3, 0, _varint(value))
    if isinstance(value, float):
        return _field(4, 1, struct.pack("<d", value))
    return _str(1, str(value))


def _key_value(key: str, value: Any) -> bytes:
    return _str(1, key) + _bytes(2, _any_value(value))


class Span:
    """One timed step. Times are nanoseconds since the epoch."""

    def __init__(self, name: str, attributes: dict[str, Any] | None = None, *,
                 trace_id: bytes | None = None, parent: Span | None = None):
        self.name, self.attributes = name, dict(attributes or {})
        self.trace_id = trace_id or (parent.trace_id if parent else secrets.token_bytes(16))
        self.span_id = secrets.token_bytes(8)
        self.parent_id = parent.span_id if parent else b""
        self.start, self.finish, self.error = time.time_ns(), None, None

    def child(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        return Span(name, attributes, parent=self)

    def end(self, error: str | None = None) -> Span:
        self.finish, self.error = time.time_ns(), error
        return self

    def encode(self) -> bytes:
        out = _bytes(1, self.trace_id) + _bytes(2, self.span_id)
        if self.parent_id:
            out += _bytes(4, self.parent_id)
        out += _str(5, self.name) + _field(6, 0, _varint(1))  # SPAN_KIND_INTERNAL
        out += _fixed64(7, self.start) + _fixed64(8, self.finish or time.time_ns())
        for key, value in self.attributes.items():
            out += _bytes(9, _key_value(key, value))
        status = (_str(2, self.error) + _field(3, 0, _varint(2))) if self.error else _field(3, 0, _varint(1))
        return out + _bytes(15, status)


def export_request(spans: list[Span], service: str) -> bytes:
    """An ExportTraceServiceRequest holding the spans under one resource and scope."""
    resource = _bytes(1, _key_value("service.name", service))
    scope = _bytes(1, _str(1, "agent-stack-train") + _str(2, "1"))
    scope_spans = scope + b"".join(_bytes(2, s.encode()) for s in spans)
    return _bytes(1, _bytes(1, resource) + _bytes(2, scope_spans))


# --- Octo -----------------------------------------------------------------

class Phoenix:
    def __init__(self, key: str, base: str = BASE, service: str = "agent-stack-train"):
        self.key, self.base, self.service = key, base.rstrip("/"), service
        self.workspace = self._call("GET", "/capabilities")["token"]["workspaceId"]

    @classmethod
    def from_env(cls, service: str = "agent-stack-train") -> Phoenix | None:
        key = os.environ.get(KEY_ENV)
        return cls(key, service=service) if key else None

    def _call(self, method: str, path: str, body: bytes | None = None, content_type: str = "application/json",
              params: dict | None = None):
        url = self.base + path + ("?" + urllib.parse.urlencode(params) if params else "")
        request = urllib.request.Request(url, data=body, method=method, headers={
            "Authorization": f"Bearer {self.key}", "Content-Type": content_type,
            "User-Agent": "agent-stack-train-otlp"})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        try:
            return json.loads(raw.decode() or "null")
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

    def send(self, spans: list[Span]) -> None:
        self._call("POST", f"/workspaces/{self.workspace}/otel/v1/traces",
                   export_request(spans, self.service), "application/x-protobuf")

    def annotate(self, span: Span, name: str, *, label: str, score: float, explanation: str = "",
                 kind: str = "CODE", metadata: dict | None = None) -> None:
        """Attach an eval score to a span already sent. kind is CODE, LLM or HUMAN."""
        record = {"span_id": span.span_id.hex(), "name": name, "annotator_kind": kind,
                  "result": {"label": label, "score": score, "explanation": explanation},
                  "metadata": metadata or {}}
        self._call("POST", f"/workspaces/{self.workspace}/otel/v1/span_annotations",
                   json.dumps({"data": [record]}).encode())

    def link(self) -> str:
        return self._call("GET", f"/workspaces/{self.workspace}/otel/link")["url"]
