import numpy as np
import matplotlib.pyplot as plt
import ipdb
from scipy.linalg import qr_multiply
from scipy.stats import chi

N    = 1000
R 	 = 1000#*5
D    = 3

base = np.array([1,1,1])

def true_kernel(x, y):
	return np.e**(-((x-y)**2/2).sum())

w    = np.random.normal(loc=0, scale=1, size=(R, D))
w   -= np.mean(w, axis=0)
w   /= w.std()
b    = np.random.uniform(0, 2*np.pi, size=R)
# b    = np.pi*np.random.randint(2, size=R)
multi_b    = [np.random.uniform(0, 2*np.pi, size=R) for _ in range(10)]
# b 	-= bmean
norm = 1./ np.sqrt(R)

def z(x):
	return -norm * np.sqrt(2) * np.cos(x @ w.T + b)
	# return -norm * np.sqrt(2) * np.cos(((w-x)**2).sum(axis=-1) + b)

def rff_kernel(x, y):
	return z(x).T@z(y)

def multi_z(x):
    return -norm * np.sqrt(2) * np.hstack([np.cos(x @ w.T + b) for b in multi_b])
    # return -norm * np.sqrt(2) * np.cos(((w-x)**2).sum(axis=-1) + b)

def multi_rff_kernel(x, y):
    return z(x).T@z(y)

class ORF: 
    def __init__(self):

        self.use_offset=True#False
        n_features = R
        size = (n_features, n_features)
        self.n_components = 100
        n_stacks = int(np.ceil(self.n_components/n_features))
        n_components = n_stacks * n_features
        random_weights_ = []
        # for _ in range(n_stacks):
        W = np.random.normal(loc=0, size=size)#distribution(random_state, size)
        S = np.diag(chi.rvs(df=n_features, size=n_features))
        SQ, _ = qr_multiply(W, S)
        random_weights_ += [SQ]

        # self.random_weights_ = np.vstack(random_weights_).T   
        self.random_weights_ = SQ.T/2 + SQ/2  
        self.random_offset_  = None
        gamma = 1.0 / D
        # self.random_weights_ *= np.sqrt(2*gamma)
        if self.use_offset:
            # self.random_offset_ = np.random.uniform(
            #     0, 2*np.pi, size=n_components
            # )

            self.random_offset_ = np.pi*np.random.randint(2, size=n_components)
        self.random_weights_ = self.random_weights_[:,:D]
        # ipdb.set_trace()

    def transform(self, X):
        gamma = 1.0 / D
        output = X@self.random_weights_.T#@X
        if self.use_offset:
            output = np.cos(output+self.random_offset_)
        else:
            output = np.hstack((np.cos(output), np.sin(output)))
        # output *= np.sqrt(2)
        # return output / np.sqrt(self.n_components)
        # return output / np.sqrt(self.random_weights_.shape[0]*(1 if self.use_offset else 2))
        return output / np.sqrt(self.random_weights_.shape[0])

orf_weights = ORF()
zorf        = orf_weights.transform
orf_kernel  = lambda x, y: zorf(x).T@zorf(y)

min_val = -10
max_val =  10
vals = [min_val + (max_val-min_val)*i/N for i in range(N)]
true_kernel_y 	= [ true_kernel(x*base, 0*base) for x in vals  ]
rff_kernel_y 	= [  rff_kernel(x*base, 0*base) for x in vals  ]
# multi_rff_kernel_y    = [  multi_rff_kernel(x*base, 0*base) for x in vals  ]
orf_kernel_y    = [  orf_kernel(x*base, 0*base) for x in vals  ]


plt.plot(vals, true_kernel_y, color="g",label="Gaussian")
plt.plot(vals,  rff_kernel_y, color="r",label="RFF approximation")
plt.plot(vals,  orf_kernel_y, color="b",label="ORF approximation")
# plt.plot(vals,  multi_rff_kernel_y, color="b",label="Multi RFF approximation")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.show()