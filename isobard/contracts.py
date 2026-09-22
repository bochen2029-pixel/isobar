"""The typed objects — the single definition (docs/contracts/objects.md; r0.2 deltas in CHANGES_r0.2.md).

Every handoff between organs is one of these. Field order is normative: it fixes canonical JSON
and therefore the content address. Times are UTC nanoseconds. Money is minor units + ISO 4217.

Laws that live here as code:
  * a probability is a distribution the multiverse samples; nothing in this module compares one
    to a constant (that is the gate's job and only the gate's);
  * an Effect without an inverse must say "irreversible" — the schema refuses anything else;
  * a hand observation carries two trusts — the envelope's (the owner's act) and the payload's
    (its origin) — and they are separate fields, compiled separately (L3, L18);
  * every derived object names what it depends on, so a reinterpretation invalidates a cone and
    never a rescan (SPEC r0.2 §10.4).
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ----------------------------------------------------------------------------------------------
# canonical JSON and content addresses
# ----------------------------------------------------------------------------------------------
def canon(obj: Any) -> str:
    """Canonical JSON: sorted keys, no whitespace, UTF-8 preserved. The hash preimage."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def blake128(data: bytes) -> str:
    return hashlib.blake2b(data, digest_size=16).hexdigest()


def content_id(obj: BaseModel, exclude: set[str] | frozenset[str] = frozenset()) -> str:
    """blake2b-128 over the canonical JSON of the object minus late-bound fields."""
    d = obj.model_dump(mode="json", exclude=set(exclude) | {"id"})
    return blake128(canon(d).encode("utf-8"))


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=False, use_enum_values=True)


# ----------------------------------------------------------------------------------------------
# enums (closed vocabularies)
# ----------------------------------------------------------------------------------------------
Lane = Literal["mail", "cal", "list", "hand", "tick", "compose", "contacts", "money", "location"]
Trust = Literal["operator", "trusted", "untrusted"]
Provenance = Literal["HIGH", "MOD", "LOW_absent", "LOW_conflict"]
Kind = Literal["deliverable", "payment", "quote", "response", "appointment", "document", "approval", "purchase", "other"]
State = Literal["candidate", "active", "waiting", "scheduled", "in_progress", "at_risk", "discharged", "cancelled", "superseded", "contested", "unresolved"]
EffortSource = Literal["explicit", "class_prior", "history", "owner", "model"]
Verb = Literal["SILENT", "FLAG", "ASK", "DRAFT", "ONE_CLICK", "ACT", "HOLD", "RECHECK"]
Seat = Literal["FIELD_WATCH", "COMPOSER", "SENTINEL"]
HoldVerdict = Literal["SILENT", "FLAG", "ASK", "DRAFT", "WAKE", "HOLD", "UNSAY"]
GradeKind = Literal["sent_as_is", "edited", "discarded", "undone", "ignored", "acted_within", "kept", "slipped", "replied", "silent", "paid", "complaint", "declared"]
Stratum = Literal["passive", "declared"]
ContraKind = Literal["OVERCOMMIT", "DOUBLEBOOK", "DEPENDENCY", "DEADLINE", "DUPLICATE", "TRAVEL", "PAID"]
Move = Literal["HOLD", "DECLINE", "COUNTER", "MOVE", "PROTECT", "NUDGE", "SPLIT", "DELEGATE", "DEFER", "RENEGOTIATE", "DROP"]
Relation = Literal["client", "vendor", "partner", "family", "colleague", "agent", "unknown"]
ConfirmedBy = Literal["owner", "inferred", "verdict"]
Rendering = Literal["forward", "share", "screenshot", "photo", "voice", "meeting", "drop", "paste", "sms", "list_line"]
CaptureState = Literal["SEALED", "PARSED", "LINKED", "DUPLICATE", "UNRESOLVED", "REFUSED", "RESOLVED"]
Refusal = Literal["ASR_FAILED", "OCR_EMPTY", "UNSUPPORTED_MEDIA", "PAYLOAD_TOO_LARGE", "EMPTY"]
NoteKind = Literal["correction", "policy_hint", "hypothesis", "question", "look_instruction", "none"]
GradeCase = Literal["seen_dismissed", "unseen", "seen_in_state"]


# ----------------------------------------------------------------------------------------------
# the tape's leaf objects
# ----------------------------------------------------------------------------------------------
class Observation(Strict):
    """Immutable raw evidence. `id` is the content address over everything but `id` itself."""
    id: str = ""
    lane: Lane
    source: str
    external_id: str
    src_rev: int = 0
    occurred_ns: int
    ingested_ns: int
    actor_ids: list[str] = Field(default_factory=list)
    thread_id: Optional[str] = None
    payload_ref: str                      # blob path or inline: "inline:" + text
    digest: str                           # blake2b-128 of the payload bytes
    intake_trust: Trust = "untrusted"     # the PAYLOAD's trust, from its origin
    envelope_trust: Trust = "untrusted"   # the ACT's trust: operator on the hand lane, never lowered by the payload
    declared: bool = False                # the hand's implicit imperative: ingest, integrate, recompute
    rendering: Optional[Rendering] = None
    note: Optional[str] = None            # the owner's words above a forward or before a recording: TESTIMONY
    telemetry: Optional[dict[str, Any]] = None
    injection_shape: bool = False

    def with_id(self) -> "Observation":
        # the receipt time and the derived injection flag are late-bound: the same external item admitted on a
        # later tick MUST get the same id, or every tick re-admits the world (found the first time ticks ran)
        self.id = content_id(self, exclude={"ingested_ns", "injection_shape"})
        return self


class CellField(Strict):
    value: Any
    p: float = Field(ge=0.0, le=1.0)
    provenance: Provenance = "MOD"


class Cell(Strict):
    """The reflex's typed output for one observation. Probabilities are sampled, never thresholded."""
    id: str = ""
    observation_id: str
    provider: str
    provider_fp: str
    questions_version: int
    question_set: str = "mail"
    fields: dict[str, CellField]
    latency_us: int = 0
    depends_on: list[str] = Field(default_factory=list)

    def with_id(self) -> "Cell":
        self.id = content_id(self, exclude={"latency_us"})
        return self


class JoinCandidate(Strict):
    kind: Literal["commitment", "actor", "thread", "money_object"]
    id: str
    p: float = Field(ge=0.0, le=1.0)


class Join(Strict):
    observation_id: str
    candidates: list[JoinCandidate] = Field(default_factory=list)
    method: Literal["exact", "lexical", "embed_rerank_reflex", "none"] = "none"
    exact_key: Optional[str] = None
    depends_on: list[str] = Field(default_factory=list)


class Due(Strict):
    earliest_ns: Optional[int] = None
    latest_ns: Optional[int] = None
    p_hard: float = Field(default=0.0, ge=0.0, le=1.0)


class Effort(Strict):
    opt_min: int
    nom_min: int
    cons_min: int
    source: EffortSource = "class_prior"
    confidence: Literal["high", "medium", "low"] = "low"

    @model_validator(mode="after")
    def _ordered(self) -> "Effort":
        if not (0 < self.opt_min <= self.nom_min <= self.cons_min):
            raise ValueError("effort must satisfy 0 < opt <= nom <= cons")
        return self


class Commitment(Strict):
    """The canonical object. Direction is debtor/creditor, never a flag."""
    id: str
    debtor_actor: str
    creditor_actor: str
    kind: Kind
    deliverable_text: str
    project: Optional[str] = None
    money_object: Optional[str] = None
    release_ns: Optional[int] = None
    due: Due = Field(default_factory=Due)
    effort: Effort = Field(default_factory=lambda: Effort(opt_min=15, nom_min=30, cons_min=60))
    dependencies: list[str] = Field(default_factory=list)
    required_seats: list[str] = Field(default_factory=list)
    tier_key: Optional[str] = None
    state: State = "candidate"
    evidence: list[str] = Field(default_factory=list)
    p_promoted: float = Field(default=0.0, ge=0.0, le=1.0)
    state_version: int = 0
    thread_id: Optional[str] = None
    depends_on: list[str] = Field(default_factory=list)
    capture_id: Optional[str] = None      # set when the row IS an unresolved capture


class Contra(Strict):
    a: int
    b: Optional[int] = None
    kind: ContraKind
    weight: float
    p: Optional[float] = None


class Arithmetic(Strict):
    bytes: float
    ms: float
    gbs: float
    peak_gbs: float
    fraction: float


class Field_(Strict):
    """The solver's output for one tick — the IR of the horizon. Stored on the tape as deltas."""
    tick_id: int
    state_version: int
    N: int
    M: int
    v: list[float]
    u: list[float]
    es: list[float]
    risk: list[float]
    argmax_cell: list[int]
    contra: list[Contra] = Field(default_factory=list)
    stock_prices: dict[str, float] = Field(default_factory=dict)
    binding_days: list[str] = Field(default_factory=list)
    delta_v_norm: float = 0.0
    arithmetic: Optional[Arithmetic] = None
    iters: int = 0
    arm: int = 0
    depends_on: list[str] = Field(default_factory=list)


class Hold(Strict):
    """LIFELINE v5 §6.3, verbatim. Written at every boundary whether or not the seat spoke."""
    boundary_id: int
    lane: Lane
    tape_pos: int
    seat: Seat
    margins: dict[str, float]
    verdict: HoldVerdict
    reason: str
    gear: int = Field(ge=0, le=3)
    latency_us: int = 0
    aired: Optional[list[str]] = None
    killed: Optional[str] = None
    trigger: Literal["evidence", "key", "tick"] = "evidence"


class Verdict(Strict):
    intent_id: str
    verb: Verb
    reason: str
    cls: str
    licence_rung: str
    exposure_after: float
    inverse_window_s: Optional[int] = None
    gate_build_hash: str
    state_version: int


class Effect(Strict):
    id: str
    intent_id: str
    target: str
    payload: dict[str, Any]
    inverse: dict[str, Any] | Literal["irreversible"]
    precondition: dict[str, Any]
    idempotency_key: str
    hold_window_s: int = 0
    state: Literal["planned", "held", "fired", "verified", "failed", "unknown", "unwound"] = "planned"
    held_reason: Optional[str] = None     # e.g. NETWORK_ABSENT on the island

    @field_validator("inverse")
    @classmethod
    def _inverse_present(cls, v: Any) -> Any:
        if v == "irreversible" or (isinstance(v, dict) and v):
            return v
        raise ValueError("an effect carries its inverse or says 'irreversible'")


class Wager(Strict):
    effect_id: Optional[str] = None
    commitment_id: str
    forecast_p: float = Field(ge=0.0, le=1.0)
    forecast_lo: float = Field(ge=0.0, le=1.0)
    forecast_hi: float = Field(ge=0.0, le=1.0)
    horizon_ns: int
    shown: bool = False
    graded_ns: Optional[int] = None
    outcome: Optional[GradeKind] = None


class Grade(Strict):
    subject: Literal["effect", "wake", "draft", "wager", "move", "cell", "commitment"]
    subject_id: str
    kind: GradeKind
    stratum: Stratum = "passive"          # declared grades never widen a licence; passive ones may
    diff: Optional[str] = None
    t_delta_s: Optional[int] = None
    salted: bool = False
    ns: int
    case: Optional[GradeCase] = None      # for declared grades: which of the three hand cases


# ----------------------------------------------------------------------------------------------
# the hand lane (SPEC r0.2 §5)
# ----------------------------------------------------------------------------------------------
class Capture(Strict):
    """One hand event and the state it reached. Every capture ends in a terminal state or the audit names it."""
    id: str                               # = the observation id
    rendering: Rendering
    state: CaptureState
    sealed_ns: int
    receipt: str                          # the first eight hex of the sealing row's hash
    refusal: Optional[Refusal] = None
    linked_to: Optional[str] = None       # commitment id on LINKED / RESOLVED
    duplicate_of: Optional[str] = None    # observation id on DUPLICATE
    resolved_ns: Optional[int] = None
    join_method: Optional[str] = None
    note_kind: NoteKind = "none"
    grade_case: Optional[GradeCase] = None
    unresolved_row: Optional[str] = None  # the commitment id of the row carried in the UNRESOLVED stock
    keys: dict[str, str] = Field(default_factory=dict)   # forward_key, quoted_digest, original_mid, ids found


class HandReply(Strict):
    """The typed reply the address sends back. Never prose beyond these lines."""
    capture_id: str
    sealed: str
    moved: Optional[str] = None
    linked: Optional[str] = None
    unresolved: bool = False
    duplicate_of: Optional[str] = None
    ask: Optional[str] = None
    refused: Optional[str] = None
    held: Optional[str] = None            # NETWORK_ABSENT: the reply is queued, not sent

    def render(self) -> str:
        lines = [f"sealed   {self.sealed}"]
        if self.moved:
            lines.append(f"moved    {self.moved}")
        if self.linked:
            lines.append(f"linked   {self.linked}")
        elif self.duplicate_of:
            lines.append(f"linked   duplicate of {self.duplicate_of}")
        elif self.unresolved:
            lines.append("linked   unresolved (re-asked each tick)")
        lines.append(f"ask?     {self.ask or 'none'}")
        if self.refused:
            lines.append(f"refused  {self.refused} (payload sealed; try again or type it)")
        if self.held:
            lines.append(f"held     {self.held}")
        return "\n".join(lines)


class CoverageGap(Strict):
    """A hand event the plane had no way to see: names the channel it lacks."""
    capture_id: str
    channel: str                          # e.g. "domain:portal.example" | "app:whatsapp" | "modality:voice"
    sender: Optional[str] = None
    ns: int


# ----------------------------------------------------------------------------------------------
# registries (docs/contracts/registry.md)
# ----------------------------------------------------------------------------------------------
class Identity(Strict):
    kind: Literal["email", "phone", "handle", "external_id", "voice"]
    value: str
    source: str = ""
    first_seen_ns: int = 0


class ReplyLatency(Strict):
    n: int = 0
    p10_s: Optional[int] = None
    p50_s: Optional[int] = None
    p90_s: Optional[int] = None


class ActorStats(Strict):
    arrivals_per_week: float = 0.0
    reply_latency: ReplyLatency = Field(default_factory=ReplyLatency)
    promises_kept: int = 0
    promises_slipped: int = 0


class Actor(Strict):
    id: str
    kind: Literal["person", "org", "agent"] = "person"
    identities: list[Identity] = Field(default_factory=list)
    display_name: str = ""
    org_id: Optional[str] = None
    tier: Literal[1, 2, 3, 4, 0] = 0          # 0 = unknown; tier is OWNER POLICY (tiers.yaml)
    relation: Relation = "unknown"
    places: list[str] = Field(default_factory=list)
    stats: ActorStats = Field(default_factory=ActorStats)
    silence_price_floor: float = 0.3
    never_auto_contact: bool = False
    confirmed_by: ConfirmedBy = "inferred"
    provenance: list[str] = Field(default_factory=list)


class TravelEdge(Strict):
    to: str
    minutes: int
    source: Literal["routing", "owner", "history"] = "owner"
    cached_ns: int = 0


class Place(Strict):
    id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius_m: Optional[int] = None
    address: Optional[str] = None
    role: Literal["home", "work", "client", "vendor", "site", "frequent", "sensitive", "transit"] = "frequent"
    actors: list[str] = Field(default_factory=list)
    travel_edges: list[TravelEdge] = Field(default_factory=list)
    confirmed_by: ConfirmedBy = "inferred"
    provenance: list[str] = Field(default_factory=list)


class MoneyObject(Strict):
    id: str
    kind: Literal["quote", "proposal", "invoice", "bill", "payment", "credit", "refund"]
    counterparty: str
    amount_minor: Optional[int] = None
    currency: Optional[str] = None
    issued_ns: Optional[int] = None
    due_ns: Optional[int] = None
    status: Literal["draft", "sent", "acknowledged", "accepted", "declined", "paid", "partially_paid", "overdue", "unknown"] = "unknown"
    status_source: Literal["verdict_connector", "mail_inference", "owner"] = "mail_inference"
    payment_status_connected: bool = False
    evidence: list[str] = Field(default_factory=list)
    commitment_id: Optional[str] = None
    confirmed_by: ConfirmedBy = "inferred"
    provenance: list[str] = Field(default_factory=list)


# ----------------------------------------------------------------------------------------------
# the scan's finding (the X-ray's row)
# ----------------------------------------------------------------------------------------------
FindingType = Literal["SILENT_QUOTE", "SILENT_PROPOSAL", "APPARENT_OVERDUE_INVOICE", "CUSTOMER_WAITING",
                      "WE_ARE_WAITING", "PROMISE_PAST_DUE", "UNRESOLVED_REQUEST", "MISSING_RESPONSE", "DUPLICATE",
                      "UNRESOLVED_CAPTURE"]


class Finding(Strict):
    finding_type: FindingType
    commitment_id: Optional[str] = None
    counterparty: str
    counterparty_tier: int = 0
    amount_minor: Optional[int] = None
    currency: Optional[str] = None
    payment_status_connected: bool = False
    sent_ns: Optional[int] = None
    last_meaningful_reply_ns: Optional[int] = None
    days_silent: Optional[float] = None
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    recommendation: Literal["FOLLOW_UP", "REPLY", "DO", "REVIEW", "MERGE", "NONE", "RESOLVE"] = "REVIEW"
    why: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


ALL_MODELS = [Observation, CellField, Cell, JoinCandidate, Join, Due, Effort, Commitment, Contra, Arithmetic,
              Field_, Hold, Verdict, Effect, Wager, Grade, Capture, HandReply, CoverageGap, Identity, ReplyLatency,
              ActorStats, Actor, TravelEdge, Place, MoneyObject, Finding]
