import matplotlib.legend as mlegend
from matplotlib import _api
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.offsetbox import (
    DrawingArea,
    HPacker,
    TextArea,
    VPacker,
)


class MatrixLegend(mlegend.Legend):
    def __init__(self, parent, handles, labels, row_col_delimiter: str = "|", **legend_kwargs):
        self._row_col_delimiter = row_col_delimiter
        legend_kwargs.setdefault("columnspacing", 0.5)  # type: ignore
        super().__init__(parent, handles, labels, **legend_kwargs)

    def _row_col_labels(self, label: str) -> tuple[str, str]:
        row, col = label.split(self._row_col_delimiter)
        return row.strip(), col.strip()

    def _init_legend_box(self, handles, labels, markerfirst=True):
        """
        Initialize the legend_box. The legend_box is an instance of
        the OffsetBox, which is packed with legend handles and
        texts. Once packed, their location is calculated during the
        drawing time.
        """

        fontsize = self._fontsize

        # legend_box is a HPacker, horizontally packed with columns.
        # Each column is a VPacker, vertically packed with legend items.
        # Each legend item is a HPacker packed with:
        # - handlebox: a DrawingArea which contains the legend handle.
        # - labelbox: a TextArea which contains the legend text.

        text_list = []  # the list of text instances
        handle_list = []  # the list of handle instances

        # The approximate height and descent of text. These values are
        # only used for plotting the legend handle.
        # descent = 0.35 * fontsize * (self.handleheight - 0.7)  # heuristic.
        # height = fontsize * self.handleheight - descent
        descent = 0.0
        height = fontsize
        # each handle needs to be drawn inside a box of (x, y, w, h) =
        # (0, -descent, width, height).  And their coordinates should
        # be given in the display coordinates.

        # The transformation of each handle will be automatically set
        # to self.get_transform(). If the artist does not use its
        # default transform (e.g., Collections), you need to
        # manually set their transform to the self.get_transform().
        legend_handler_map = self.get_legend_handler_map()

        row_labels = []
        col_labels = []
        for label in labels:
            try:
                rl, cl = self._row_col_labels(label)
            except ValueError:
                print(f"Ignoring label: {label}")
                continue
            if rl not in row_labels:
                row_labels.append(rl)
            if cl not in col_labels:
                col_labels.append(cl)
        inner_matrix: list[list[Artist | None]] = [
            [None for _ in range(len(col_labels))] for _ in range(len(row_labels))
        ]

        for orig_handle, label in zip(handles, labels):
            handler = self.get_legend_handler(legend_handler_map, orig_handle)
            if handler is None:
                _api.warn_external(
                    "Legend does not support handles for "
                    f"{type(orig_handle).__name__} "
                    "instances.\nA proxy artist may be used "
                    "instead.\nSee: https://matplotlib.org/"
                    "stable/users/explain/axes/legend_guide.html"
                    "#controlling-the-legend-entries"
                )
                continue
            rl, cl = self._row_col_labels(label)
            i = row_labels.index(rl)
            j = col_labels.index(cl)

            handlebox = DrawingArea(width=self.handlelength * fontsize, height=height, xdescent=0.0, ydescent=descent)
            inner_matrix[i][j] = handlebox
            handle_list.append(handler.legend_artist(self, orig_handle, fontsize, handlebox))

        columns = []

        # row labels
        rl_artists = [
            TextArea(
                "",
                multilinebaseline=True,
                textprops=dict(verticalalignment="baseline", horizontalalignment="right", fontproperties=self.prop),
            )
        ]
        for rl in row_labels:
            text_area = TextArea(
                rl,
                multilinebaseline=True,
                textprops=dict(verticalalignment="baseline", horizontalalignment="right", fontproperties=self.prop),
            )
            text_list.append(text_area._text)
            rl_artists.append(text_area)

        columns.append(VPacker(pad=0, sep=self.labelspacing * fontsize, align="baseline", children=rl_artists))

        for col, cl in enumerate(col_labels):
            text_area = TextArea(
                cl,
                multilinebaseline=True,
                textprops=dict(verticalalignment="baseline", horizontalalignment="left", fontproperties=self.prop),
            )
            text_list.append(text_area._text)
            col_artists = [text_area]
            for i in range(len(row_labels)):
                col_artists.append(inner_matrix[i][col])
            columns.append(VPacker(pad=0, sep=self.labelspacing * fontsize, align="center", children=col_artists))

        mode = "expand" if self._mode == "expand" else "fixed"
        sep = self.columnspacing * fontsize
        self._legend_handle_box = HPacker(pad=0, sep=sep, align="baseline", mode=mode, children=columns)
        self._legend_title_box = TextArea("")
        self._legend_box = VPacker(
            pad=self.borderpad * fontsize,
            sep=self.labelspacing * fontsize,
            align=self._alignment,
            children=[self._legend_title_box, self._legend_handle_box],
        )
        self._legend_box.set_figure(self.get_figure(root=False))
        self._legend_box.axes = self.axes
        self.texts = text_list
        self.legend_handles = handle_list


def matrix_legend(ax: Axes, *args, **kwargs) -> MatrixLegend:
    """Drop-in replacement for ax.legend(*args, **kwargs)"""
    handles, labels, kwargs = mlegend._parse_legend_args([ax])
    ml = MatrixLegend(ax, handles, labels, **kwargs)
    ax.legend_ = ml
    ax.legend_._remove_method = ax._remove_legend
    return ml
