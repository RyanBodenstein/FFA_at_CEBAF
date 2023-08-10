import numpy as np

rel = [[str(i + j) for i in range(101)] for j in range(1,7)]
nrel = np.array(rel)

print(nrel.shape())