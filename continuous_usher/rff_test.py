import numpy as np
import matplotlib.pyplot as plt
import pdb

N    = 1000
R 	 = 200
D    = 3

base = np.array([1,1,1])

def true_kernel(x, y):
	return np.e**(-((x-y)**2/2).sum())

w    = np.random.normal(loc=0, scale=1, size=(R, D))
# wmean= np.mean(w, axis=0)
# w 	-= wmean
# w   /= w.std()
b    = np.random.uniform(0, 2*np.pi, size=R)
# bmean= np.mean(b, axis=0)
# b 	-= bmean
norm = 1./ np.sqrt(R)

def z(x):
	return -norm * np.sqrt(2) * np.cos(w @ x.T + b)

def rff_kernel(x, y):
	return z(x).T@z(y)

min_val = -50
max_val = 50
vals = [min_val + (max_val-min_val)*i/N for i in range(N)]
true_kernel_y 	= [ true_kernel(x*base, 0*base) for x in vals  ]
rff_kernel_y 	= [  rff_kernel(x*base, 0*base) for x in vals  ]


plt.plot(vals, true_kernel_y, color="g",label="Gaussian")
plt.plot(vals,  rff_kernel_y, color="r",label="RFF approximation")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.show()