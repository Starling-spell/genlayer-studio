"""`current_state.reroute_to` pins a contract to a GenVM executor version.

It is written once, when the deploy is registered, and every later execution
picks it up through the contract snapshot.
"""

from sqlalchemy.orm import Session

from backend.database_handler.contract_processor import ContractProcessor
from backend.database_handler.contract_snapshot import ContractSnapshot
from backend.database_handler.models import CurrentState


def _empty_state() -> dict:
    return {"state": {"accepted": {}, "finalized": {}}}


def test_register_contract_persists_reroute_to(session: Session):
    address = "0xreroute"
    session.add(CurrentState(id=address, data={}))
    session.commit()

    ContractProcessor(session).register_contract(
        {"id": address, "data": _empty_state(), "reroute_to": "v0.2.17"}
    )

    assert ContractSnapshot(address, session).reroute_to == "v0.2.17"


def test_register_contract_without_reroute_to(session: Session):
    address = "0xnoreroute"
    session.add(CurrentState(id=address, data={}))
    session.commit()

    ContractProcessor(session).register_contract(
        {"id": address, "data": _empty_state(), "reroute_to": None}
    )

    assert ContractSnapshot(address, session).reroute_to is None


def test_reroute_to_survives_state_updates(session: Session):
    address = "0xrerouteupdate"
    session.add(CurrentState(id=address, data=_empty_state(), reroute_to="v0.2.17"))
    session.commit()

    ContractProcessor(session).update_contract_state(
        address, accepted_state={"aaa": "bbb"}
    )

    assert ContractSnapshot(address, session).reroute_to == "v0.2.17"


def test_snapshot_round_trip_keeps_reroute_to(session: Session):
    address = "0xreroutesnapshot"
    session.add(CurrentState(id=address, data=_empty_state(), reroute_to="v0.2.17"))
    session.commit()

    snapshot = ContractSnapshot(address, session)
    restored = ContractSnapshot.from_dict(snapshot.to_dict())

    assert restored.reroute_to == "v0.2.17"
