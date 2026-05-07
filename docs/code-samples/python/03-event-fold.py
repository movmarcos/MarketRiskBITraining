# Module: 03 — The Trade Lifecycle (Risk Lens)
# Purpose:  Fold a long-format trade event log into a wide "current state"
#           DataFrame as of a chosen timestamp. Handles BOOK / AMEND / CANCEL /
#           TERMINATE. Intended for ad-hoc reconciliation, not production EOD.
# Depends:  pandas (3.11+), numpy (transitively).
# Run:      python docs/code-samples/python/03-event-fold.py

from __future__ import annotations

import json
import pandas as pd


def fold_events_to_position(
    events: pd.DataFrame,
    as_of: pd.Timestamp,
) -> pd.DataFrame:
    """Collapse an event log into one row per active trade as of ``as_of``.

    Parameters
    ----------
    events :
        Long-format event log. Expected columns:
        ``trade_id`` (str), ``event_seq`` (int), ``event_type`` (str),
        ``event_ts`` (datetime64[ns]), ``business_date`` (date-like),
        ``payload_json`` (str).
        ``event_type`` is one of: ``BOOK``, ``AMEND``, ``CANCEL``, ``TERMINATE``.
    as_of :
        Wall-clock cutoff. Events with ``event_ts > as_of`` are ignored.

    Returns
    -------
    pd.DataFrame
        One row per ``trade_id`` that is still active at ``as_of``. Columns:
        ``trade_id``, ``status``, ``last_event_type``, ``last_event_ts``,
        ``business_date``, plus the keys of the latest ``payload_json``.
    """
    if events.empty:
        return events.iloc[0:0]

    # 1. Apply the cutoff. Events stamped strictly after the as-of are unseen.
    in_scope = events.loc[events["event_ts"] <= as_of].copy()

    # 2. Stable ordering: by event_ts, then event_seq to break same-ts ties.
    in_scope = in_scope.sort_values(
        by=["trade_id", "event_ts", "event_seq"],
        kind="mergesort",
    )

    # 3. Take the last event per trade — that is the trade's current state.
    last = in_scope.groupby("trade_id", as_index=False).tail(1)

    # 4. Drop trades whose terminal event removes them from the active book.
    active = last.loc[~last["event_type"].isin(["CANCEL", "TERMINATE"])].copy()

    # 5. Project payload_json keys into columns. Latest event wins by design.
    payloads = active["payload_json"].apply(json.loads).apply(pd.Series)
    out = pd.concat(
        [
            active[["trade_id", "event_type", "event_ts", "business_date"]]
            .rename(columns={"event_type": "last_event_type",
                             "event_ts": "last_event_ts"})
            .reset_index(drop=True),
            payloads.reset_index(drop=True),
        ],
        axis=1,
    )

    # 6. Surface a single status column. AMEND lands the trade back in NEW
    #    (per the convention in section 3.2); BOOK is also NEW.
    out["status"] = "NEW"

    # Stable column order.
    head = ["trade_id", "status", "last_event_type", "last_event_ts",
            "business_date"]
    tail = [c for c in out.columns if c not in head]
    return out[head + tail].sort_values("trade_id").reset_index(drop=True)


if __name__ == "__main__":
    sample = pd.DataFrame(
        [
            # T-1: BOOK then AMEND — should appear with amended notional.
            {"trade_id": "T-1", "event_seq": 1, "event_type": "BOOK",
             "event_ts": pd.Timestamp("2026-05-06 09:30"),
             "business_date": "2026-05-06",
             "payload_json": '{"notional": 100000000, "rate": 0.0425, "ccy": "USD"}'},
            {"trade_id": "T-1", "event_seq": 2, "event_type": "AMEND",
             "event_ts": pd.Timestamp("2026-05-07 11:15"),
             "business_date": "2026-05-07",
             "payload_json": '{"notional": 80000000, "rate": 0.0430, "ccy": "USD"}'},
            # T-2: BOOK then CANCEL — should drop out entirely.
            {"trade_id": "T-2", "event_seq": 1, "event_type": "BOOK",
             "event_ts": pd.Timestamp("2026-05-06 10:00"),
             "business_date": "2026-05-06",
             "payload_json": '{"notional": 25000000, "rate": 0.0410, "ccy": "USD"}'},
            {"trade_id": "T-2", "event_seq": 2, "event_type": "CANCEL",
             "event_ts": pd.Timestamp("2026-05-06 16:45"),
             "business_date": "2026-05-06",
             "payload_json": '{}'},
            # T-3: BOOK then TERMINATE — drops out.
            {"trade_id": "T-3", "event_seq": 1, "event_type": "BOOK",
             "event_ts": pd.Timestamp("2026-05-05 14:00"),
             "business_date": "2026-05-05",
             "payload_json": '{"notional": 50000000, "rate": 0.0500, "ccy": "EUR"}'},
            {"trade_id": "T-3", "event_seq": 2, "event_type": "TERMINATE",
             "event_ts": pd.Timestamp("2026-05-07 09:00"),
             "business_date": "2026-05-07",
             "payload_json": '{"notional": 50000000, "rate": 0.0500, "ccy": "EUR"}'},
            # T-4: untouched BOOK — should appear unchanged.
            {"trade_id": "T-4", "event_seq": 1, "event_type": "BOOK",
             "event_ts": pd.Timestamp("2026-05-07 08:15"),
             "business_date": "2026-05-07",
             "payload_json": '{"notional": 15000000, "rate": 0.0395, "ccy": "GBP"}'},
        ]
    )

    as_of = pd.Timestamp("2026-05-07 17:00")
    state = fold_events_to_position(sample, as_of)

    print(f"Active book as of {as_of}:")
    print(state.to_string(index=False))
