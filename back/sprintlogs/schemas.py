from enum import StrEnum

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
