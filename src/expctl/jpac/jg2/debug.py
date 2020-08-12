import numpy as np
import matplotlib.pyplot as plt
from .hist import H2

evt_a = np.array([list(range(10))])
# evt_b = evt_a
evt_b = np.array([[0]])

print(evt_a)
print(evt_b)

# Hab = H2([evt_a, evt_b], 10)
Hab = H2([evt_b, evt_a], 10)
print(Hab)

plt.plot(Hab, 'ro')
plt.show()
