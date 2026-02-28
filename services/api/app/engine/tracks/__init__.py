from .astrid import AstridTrackPlugin
from .base import TrackPlugin
from .jon import JonTrackPlugin

TRACK_PLUGINS: list[TrackPlugin] = [
    JonTrackPlugin(),
    AstridTrackPlugin(),
]

TRACK_REGISTRY = {plugin.student_id: plugin for plugin in TRACK_PLUGINS}


def get_track_plugin(student_id: str) -> TrackPlugin | None:
    return TRACK_REGISTRY.get(student_id)
