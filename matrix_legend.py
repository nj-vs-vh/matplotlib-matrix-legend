import matplotlib.legend as mlegend
import numpy as np
from matplotlib import _api
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.offsetbox import DrawingArea, HPacker, TextArea, VPacker
from matplotlib.text import Text


class MatrixLegend(mlegend.Legend):
    def __init__(
        self,
        parent,
        handles,
        labels,
        row_col_delimiter: str = "|",
        legend_blocks_spacing: float = 1.0,
        **legend_kwargs,
    ):
        self._row_col_delimiter = row_col_delimiter
        self._legend_blocks_spacing = legend_blocks_spacing
        legend_kwargs.setdefault("columnspacing", 0.5)  # type: ignore
        super().__init__(parent, handles, labels, **legend_kwargs)

    def _row_col_labels(self, label: str) -> tuple[str, str]:
        row, col = label.split(self._row_col_delimiter)
        return row.strip(), col.strip()

    def _is_matrix_label(self, label: str) -> bool:
        try:
            self._row_col_labels(label)
            return True
        except ValueError:
            return False

    def _make_regular_legend_box(self, handles, labels, markerfirst=True):
        """
        Copied from Legend._init_legend_box, creates regular legend but returns it's
        offset box for final composition.
        """

        fontsize = self._fontsize

        # legend_box is a HPacker, horizontally packed with columns.
        # Each column is a VPacker, vertically packed with legend items.
        # Each legend item is a HPacker packed with:
        # - handlebox: a DrawingArea which contains the legend handle.
        # - labelbox: a TextArea which contains the legend text.

        texts: list[Text] = []
        artists: list[Artist | None] = []
        handles_and_labels = []

        # The approximate height and descent of text. These values are
        # only used for plotting the legend handle.
        descent = 0.35 * fontsize * (self.handleheight - 0.7)  # heuristic.
        height = fontsize * self.handleheight - descent
        # each handle needs to be drawn inside a box of (x, y, w, h) =
        # (0, -descent, width, height).  And their coordinates should
        # be given in the display coordinates.

        # The transformation of each handle will be automatically set
        # to self.get_transform(). If the artist does not use its
        # default transform (e.g., Collections), you need to
        # manually set their transform to the self.get_transform().
        legend_handler_map = self.get_legend_handler_map()

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
                # No handle for this artist, so we just defer to None.
                artists.append(None)
            else:
                textbox = TextArea(
                    label,
                    multilinebaseline=True,
                    textprops=dict(verticalalignment="baseline", horizontalalignment="left", fontproperties=self.prop),
                )
                handlebox = DrawingArea(
                    width=self.handlelength * fontsize, height=height, xdescent=0.0, ydescent=descent
                )

                texts.append(textbox._text)
                # Create the artist for the legend which represents the
                # original artist/handle.
                artists.append(handler.legend_artist(self, orig_handle, fontsize, handlebox))
                handles_and_labels.append((handlebox, textbox))

        columnbox = []
        # array_split splits n handles_and_labels into ncols columns, with the
        # first n%ncols columns having an extra entry.  filter(len, ...)
        # handles the case where n < ncols: the last ncols-n columns are empty
        # and get filtered out.
        for handles_and_labels_column in filter(len, np.array_split(handles_and_labels, self._ncols)):
            # pack handlebox and labelbox into itembox
            itemboxes = [
                HPacker(
                    pad=0,
                    sep=self.handletextpad * fontsize,
                    children=[h, t] if markerfirst else [t, h],
                    align="baseline",
                )
                for h, t in handles_and_labels_column
            ]
            # pack columnbox
            alignment = "baseline" if markerfirst else "right"
            columnbox.append(VPacker(pad=0, sep=self.labelspacing * fontsize, align=alignment, children=itemboxes))

        mode = "expand" if self._mode == "expand" else "fixed"
        sep = self.columnspacing * fontsize
        return HPacker(pad=0, sep=sep, align="baseline", mode=mode, children=columnbox), texts, artists

    def _make_matrix_legend_box(self, handles, labels):
        fontsize = self._fontsize
        texts: list[Text] = []
        artists: list[Artist] = []
        descent = 0.0
        height = fontsize
        legend_handler_map = self.get_legend_handler_map()

        row_label_texts = []
        col_label_texts = []
        for label in labels:
            row_label, col_label = self._row_col_labels(label)
            if row_label not in row_label_texts:
                row_label_texts.append(row_label)
            if col_label not in col_label_texts:
                col_label_texts.append(col_label)
        handlebox_matrix: list[list[DrawingArea]] = [
            [
                DrawingArea(width=self.handlelength * fontsize, height=height, xdescent=0.0, ydescent=descent)
                for _ in range(len(col_label_texts))
            ]
            for _ in range(len(row_label_texts))
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
            row_label, col_label = self._row_col_labels(label)
            i = row_label_texts.index(row_label)
            j = col_label_texts.index(col_label)
            handlebox = handlebox_matrix[i][j]
            artists.append(handler.legend_artist(self, orig_handle, fontsize, handlebox=handlebox))

        columns: list[VPacker] = []

        # row labels
        rl_artists = [
            TextArea(
                "",
                multilinebaseline=True,
                textprops=dict(verticalalignment="baseline", horizontalalignment="right", fontproperties=self.prop),
            )
        ]
        for row_label in row_label_texts:
            text_area = TextArea(
                row_label,
                multilinebaseline=True,
                textprops=dict(verticalalignment="baseline", horizontalalignment="right", fontproperties=self.prop),
            )
            texts.append(text_area._text)
            rl_artists.append(text_area)

        columns.append(VPacker(pad=0, sep=self.labelspacing * fontsize, align="baseline", children=rl_artists))

        for col, col_label in enumerate(col_label_texts):
            text_area = TextArea(
                col_label,
                multilinebaseline=True,
                textprops=dict(verticalalignment="baseline", horizontalalignment="left", fontproperties=self.prop),
            )
            texts.append(text_area._text)
            col_artists = [text_area]
            for i in range(len(row_label_texts)):
                col_artists.append(handlebox_matrix[i][col])
            columns.append(VPacker(pad=0, sep=self.labelspacing * fontsize, align="center", children=col_artists))

        mode = "expand" if self._mode == "expand" else "fixed"
        sep = self.columnspacing * fontsize
        return HPacker(pad=0, sep=sep, align="baseline", mode=mode, children=columns), texts, artists

    def _init_legend_box(self, handles, labels, markerfirst=True):
        fontsize = self._fontsize

        m_handles = []
        m_labels = []
        r_handles = []
        r_labels = []
        for handle, label in zip(handles, labels):
            _handles, _labels = (m_handles, m_labels) if self._is_matrix_label(label) else (r_handles, r_labels)
            _handles.append(handle)
            _labels.append(label)

        m_box, m_texts, m_artists = self._make_matrix_legend_box(m_handles, m_labels)
        r_box, r_texts, r_artists = self._make_regular_legend_box(r_handles, r_labels)

        blocks = []
        if m_artists:
            blocks.append(m_box)
        if r_artists:
            blocks.append(r_box)
        mode = "expand" if self._mode == "expand" else "fixed"
        # TODO: add ability to use HPacker here, invert order etc
        self._legend_handle_box = VPacker(
            pad=0,
            sep=self._legend_blocks_spacing * fontsize,
            align="left",
            mode=mode,
            children=blocks,
        )

        self._legend_title_box = TextArea("")
        self._legend_box = VPacker(
            pad=self.borderpad * fontsize,
            sep=self.labelspacing * fontsize,
            align=self._alignment,
            children=[self._legend_title_box, self._legend_handle_box],
        )
        self._legend_box.set_figure(self.get_figure(root=False))
        self._legend_box.axes = self.axes
        self.texts = m_texts + r_texts
        self.legend_handles = m_artists + r_artists


def matrix_legend(
    ax: Axes,
    *ax_legend_args,
    row_col_delimeter: str = "|",
    legend_blocks_spacing: float = 1.5,
    **ax_legend_kwargs,
) -> MatrixLegend:
    """
    Drop-in replacement for ax.legend(*args, **kwargs). Handles with labels in the form of
    "row label | col label" are renderd in a matrix.
    """
    handles, labels, ax_legend_kwargs = mlegend._parse_legend_args([ax], *ax_legend_args, **ax_legend_kwargs)
    ml = MatrixLegend(
        ax,
        handles,
        labels,
        row_col_delimiter=row_col_delimeter,
        legend_blocks_spacing=legend_blocks_spacing,
        **ax_legend_kwargs,
    )
    ax.legend_ = ml
    ax.legend_._remove_method = ax._remove_legend
    return ml
