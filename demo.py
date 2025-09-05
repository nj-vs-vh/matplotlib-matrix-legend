import numpy as np
from matplotlib import pyplot as plt

from matrix_legend import matrix_legend

fig, axes = plt.subplots(ncols=2, figsize=(10, 5))

for idx, ax in enumerate(axes):
    x = np.linspace(0, 1, 30)
    for label, func, linestyle in (("sin", np.sin, "-"), ("linear", lambda x: x, "--")):
        for freq, color in ((1.0, "r"), (1.5, "g"), (2.0, "b")):
            y = func(freq * x)
            ax.plot(x, y, linestyle=linestyle, color=color, label=f"{label} | $ \\omega={freq:.2g} $")

    if idx == 0:
        ax.legend()
        ax.set_title("Regular legend")
    else:
        matrix_legend(ax)
        ax.set_title("Matrix legend")

fig.savefig("demo.png")
