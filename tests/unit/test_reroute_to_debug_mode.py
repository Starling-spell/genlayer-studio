"""`reroute_to` is only honored by the genvm manager under `debug_mode >= safe`.

Below that the manager ignores it *silently* and runs the manifest-resolved
executor instead, so both the RPC entry point and the run path refuse the
request rather than executing on the wrong executor.
"""

import asyncio

import pytest

from backend.node.genvm.base import run_genvm_host
from backend.protocol_rpc.endpoints import _validate_reroute_to
from backend.protocol_rpc.exceptions import JSONRPCError


def _run_with(reroute_to, **kwargs):
    return asyncio.run(
        run_genvm_host(
            lambda sock: None,
            timeout=1,
            is_sync=True,
            message={},
            reroute_to=reroute_to,
            **kwargs,
        )
    )


def test_run_genvm_host_rejects_reroute_to_with_debug_mode_disabled():
    with pytest.raises(ValueError, match="requires debug_mode >= safe"):
        _run_with("v0.2.17", debug_mode="disabled")


def test_run_genvm_host_rejects_reroute_to_when_capture_off_implies_disabled():
    # debug_mode unset + capture_output=False resolves to "disabled" in base_host
    with pytest.raises(ValueError, match="requires debug_mode >= safe"):
        _run_with("v0.2.17", capture_output=False)


def test_validate_reroute_to_allows_missing_value(monkeypatch):
    monkeypatch.setenv("GENVM_DEBUG_MODE", "false")
    _validate_reroute_to(None)
    _validate_reroute_to({})
    _validate_reroute_to({"reroute_to": None})


def test_validate_reroute_to_allows_value_in_debug_mode(monkeypatch):
    monkeypatch.setenv("GENVM_DEBUG_MODE", "true")
    _validate_reroute_to({"reroute_to": "v0.2.17"})


def test_validate_reroute_to_rejects_value_without_debug_mode(monkeypatch):
    monkeypatch.setattr(
        "backend.protocol_rpc.endpoints._genvm_debug_mode", lambda: "disabled"
    )
    with pytest.raises(JSONRPCError) as exc:
        _validate_reroute_to({"reroute_to": "v0.2.17"})
    assert exc.value.code == -32602
