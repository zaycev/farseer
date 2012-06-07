import matplotlib.pyplot as plt

fig = plt.figure()
ax_1 = fig.add_subplot(3,1,1)
ax_2 = fig.add_subplot(3,1,2)
ax_3 = fig.add_subplot(3,1,3)

import numpy as np
t = np.arange(-0.5, 1.5, 0.01)
s = np.sin(2*np.pi*t)
line, = ax_1.plot(t, s, color="blue", lw=1, label="test1")
line, = ax_2.plot(t, s, color="blue", lw=2, label="test1")
line, = ax_3.plot(t, s, color="blue", lw=3, label="test1")

plt.show()