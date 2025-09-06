# Matrix legend for Matplotlib

A small extension for [Matplotlib](https://matplotlib.org/)'s Legend to create
matrix legends for plots parametrized with the cartesian product of two grids.
Consider the following toy example of evaluating different functions with
different "frequency" parameter values. Full enumeration of function+parameter
pairs gets cumbersome very quickly, but the same information can be naturally
presented in a table layout.

![comparison of regular and matrix legends](https://raw.githubusercontent.com/nj-vs-vh/matplotlib-matrix-legend/refs/heads/main/images/demo.png)

## Installation

```sh
pip install matplotlib-matrix-legend
```

## Usage

The module exports one public function, a drop-in replacement for `Axes.legend`
method. Since most of the functionality is inherited directly from the original Legend class,
the styling, layout, custom handles and other features should largely work as expected.

```python
from matrix_legend import matrix_legend

fig, ax = plt.subplots()
# your plotting here

# instead of ax.legend(...)
# see https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html
# for args & kwargs
matrix_legend(ax, ...)
```
