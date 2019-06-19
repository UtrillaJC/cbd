import numpy as np

enteros = [2, 3, 4, 5, 23, 1, 255, 44, 112] #np.array([2, 3, 4, 5, 23, 1, 255, 44, 112], dtype=np.uint8)

#normalizado = enteros / 255

#print(normalizado)

s = lambda a, d: [e/d for e in a]

print(enteros <<s>> 255)
