import numpy as np
import random
enteros = [2, 3, 4, 5, 23, 1, 255, 44, 112] #np.array([2, 3, 4, 5, 23, 1, 255, 44, 112], dtype=np.uint8)
dict = {"Hola":1,"Adios":2}
print(1 in dict)
embedding_matrix = np.zeros((20, 20))
#normalizado = enteros / 255
embedding_matrix[2] = np.array(
                    range(0,20), dtype=np.float32)[:20]

print(embedding_matrix)
#print(normalizado)

s = lambda a, d: [e/d for e in a]

r = [1,2]
for n in range(0, 30):
    print(random.randint(0,3))
