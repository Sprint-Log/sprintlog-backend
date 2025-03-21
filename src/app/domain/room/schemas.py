from dataclasses import dataclass

__all__ = [
    "ParticipantInfo",
    "ParticipantInfoState",
    "ParticipantPermission",
    "Room",
    "TrackInfo",
    "TrackSource",
    "TrackType",
    "VideoLayer",
    "VideoQuality",
]


@dataclass
class ParticipantPermission:
    can_subscribe: bool
    can_publish: bool
    can_publish_data: bool


@dataclass
class VideoQuality:
    HIGH = 0
    MEDIUM = 1
    LOW = 2


@dataclass
class VideoLayer:
    quality: VideoQuality
    width: int
    height: int


@dataclass
class ParticipantInfoState:
    JOINED = 0
    DISCONNECTED = 1
    FAILED = 2
    KICKED = 3


@dataclass
class TrackType:
    AUDIO = 0
    VIDEO = 1


@dataclass
class TrackSource:
    INPUT = 0
    DATA = 1


@dataclass
class TrackInfo:
    sid: str
    type: TrackType
    source: TrackSource
    name: str | None
    mime_type: str
    muted: bool
    width: int | None
    height: int | None
    simulcast: bool
    disable_dtx: bool
    layers: list[VideoLayer]


@dataclass
class Room:
    sid: str
    name: str
    empty_timeout: str
    max_participants: str
    creation_time: str
    turn_password: str
    metadata: str | None
    num_participants: int
    active_recording: bool


@dataclass
class ParticipantInfo:
    sid: str
    identity: str
    name: str | None
    state: ParticipantInfoState
    tracks: list[TrackInfo]
    metadata: str | None
    joined_at: int
    permission: ParticipantPermission
    is_publisher: bool
