from dataclasses import dataclass


@dataclass(frozen=True)
class ChatReply:
    message: str
    suggested_hash: str | None = None
    citations: tuple[str, ...] = ()
