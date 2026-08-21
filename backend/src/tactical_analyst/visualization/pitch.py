from __future__ import annotations

from tactical_analyst.analytics.helpers import PITCH_LENGTH_M, PITCH_WIDTH_M


def create_pitch(title: str | None = None, figsize: tuple[float, float] = (9, 5.8)):
    """Create a StatsBomb-normalized metric pitch using mplsoccer when available."""

    try:
        from mplsoccer import Pitch

        pitch = Pitch(
            pitch_type="custom",
            pitch_length=PITCH_LENGTH_M,
            pitch_width=PITCH_WIDTH_M,
            line_color="#293241",
            pitch_color="#f8fafc",
        )
        fig, ax = pitch.draw(figsize=figsize, constrained_layout=True, tight_layout=False)
    except ImportError:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
        ax.set_facecolor("#f8fafc")
        ax.set_xlim(0, PITCH_LENGTH_M)
        ax.set_ylim(0, PITCH_WIDTH_M)
        ax.plot([0, PITCH_LENGTH_M, PITCH_LENGTH_M, 0, 0], [0, 0, PITCH_WIDTH_M, PITCH_WIDTH_M, 0])
        ax.axvline(PITCH_LENGTH_M / 2, color="#293241", lw=1)
        ax.set_aspect("equal")
        ax.invert_yaxis()
    ax.set_title(title or "", fontsize=12, color="#111827")
    return fig, ax


def validate_pitch_coordinates(x: float | None, y: float | None) -> bool:
    """Return whether optional coordinates are inside the normalized pitch."""

    if x is None or y is None:
        return False
    return 0 <= x <= PITCH_LENGTH_M and 0 <= y <= PITCH_WIDTH_M
