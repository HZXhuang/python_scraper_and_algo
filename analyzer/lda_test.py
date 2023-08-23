import gensim
from gensim import corpora

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import warnings
from mpl_toolkits.mplot3d import Axes3D
# warnings.filterwarnings('ignore')  # To ignore all warnings that arise here to enhance clarity

# df = pd.DataFrame(data={'id': [1, 2, 3, 4, 5], 'name': ['张三', '李四', '王五', '赵六', '李七']})
# print(df)
# print(df.sum())

fig = plt.figure()
ax = Axes3D(fig, auto_add_to_figure=False)
fig.add_axes(ax)
X = np.arange(-2, 2, 0.1)
Y = np.arange(-2, 2, 0.1)
X, Y = np.meshgrid(X, Y)


def f(x, y):
    return (1 - y**5 + x**5) * np.exp(-x**2 - y**2)


ax.plot_surface(X, Y, f(X, Y), rstride=1, cstride=1)
plt.show()
