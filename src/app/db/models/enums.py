from enum import StrEnum

__all__ = ["Category", "ItemType", "PaymentMethod", "Priority", "Progress", "Status"]


class Priority(StrEnum):
    low = "🟢"
    med = "🟡"
    hi = "🔴"


class Progress(StrEnum):
    empty = "⬜⬜⬜"
    in_progress = "🟩⬜⬜"
    half_way = "🟩🟩⬜"
    ready = "🟩🟩🟩"


class Status(StrEnum):
    new = "☀️"
    started = "🛠️"
    checked_in = "🔳"
    completed = "✅"
    cancelled = "🚫"


class Category(StrEnum):
    ideas = "💡"
    issues = "⚠️"
    maintenance = "🔨"
    finances = "💰"
    innovation = "🚀"
    bugs = "🐞"
    features = "🎁"
    security = "🔒"
    attention = "🚩"
    backend = "📡"
    database = "💾"
    desktop = "🖥️"
    mobile = "📱"
    intl = "🌍"
    design = "🎨"
    analytics = "📈"
    automation = "🤖"


class ItemType(StrEnum):
    backlog = "backlog"
    task = "task"
    draft = "draft"
    self = "self"


class PaymentMethod(StrEnum):
    K_PAY = "k-pay"
    AYA_PAY = "aya-pay"
    WAVE_PAY = "wave-pay"

class ChatType(StrEnum):
    MESSAGE = "message"
    ANNOUNCEMENT = "announcement"
    NOTE = "note"
    GROUP = "group"
    DIRECT = "direct"
    CHANNEL = "channel"

class EventType(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    JOINED = "joined"
    LEFT = "left"
    ARCHIVED = "archived"
    UNARCHIVED = "unarchived"
    PINNED = "pinned"
    UNPINNED = "unpinned"
    MENTIONED = "mentioned"
    REACTED = "reacted"
    UNREACTED = "unreacted"
    SHARED = "shared"
    UNSHARED = "unshared"


class ProjectStatus(StrEnum):
    NOT_STARTED = "not_started"  # Project is created but not yet started
    INITIATED = "initiated"  # Project is started
    ACTIVE = "active"  # Project is ongoing
    COMPLETED = "completed"  # Work is done
    ON_HOLD = "on_hold"  # Temporarily paused
    CANCELLED = "cancelled"  # Cancelled before completion
