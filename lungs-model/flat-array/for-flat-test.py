# This code compares triple-for loop and flat von neimann neighbours implementations
# and tests if this 2 methods gives the same result
# also test that 460 instead of 512 on 0-axis

# firstly i remove this condition:
            # if ro[i, j, k] < 0.1 and i != A and j != B and k != C: # refl􏰂ecting condition | use numpy masking
                # P[i, j, k] = 0

import numpy as np
from time import time

N = 16
# S = 10 # number of slices / CT-images / scans
S = 16 # first test simple case when N == S

r = np.random.random((S, N, N))
# r = np.load('r.npy')
ro  = 1e-5 + 1.24e-3*r - 2.83e-7*r*r + 2.79e-11*r*r*r
c = (ro + 0.112) * 1.38e-6

# тут не факт что все 1
l = 1 # dt
h = 1 # dx = dy = dz

K = l / h * c
K2 = K**2
K2_3_ro = K2 / 3 / ro


# initial conditions
P_pp = np.random.random((S, N, N)) # previous previous t - 2
P_p  = np.random.random((S, N, N)) # previous          t - 1

# P_pp = np.arange(N**3).reshape(N, N, N) * 10.
# P_p = np.arange(N**3).reshape(N, N, N) * 12.
# P_pp = np.load('P_pp.npy')
# P_p = np.load('P_p.npy')
# P    = np.zeros((S, N, N), dtype=np.float64) # current           t

# np.save('P_pp.npy', P_pp)
# np.save('P_p.npy', P_p)
# np.save('r.npy', r)

def old_slow1(P_pp, P_p):
    '''slow explicit n^3, c-style implementation v0.2'''
    
    S = P_p.shape[0]
    N = P_p.shape[1]

    # P[2:-2, 2:-2, 2:-2] = (2 - 7.5 * K2[2:-2, 2:-2, 2:-2]) * P_p[2:-2, 2:-2, 2:-2] - P_pp[2:-2, 2:-2, 2:-2]
    # P = np.zeros_like(P_p)

    P = (2 - 7.5 * K2) * P_p - P_pp


    for i in range(2, S - 2):
        for j in range(2, N - 2):
            for k in range(2, N - 2):
                s1 = (P_p[i + 1, j    , k    ] + \
                      P_p[i - 1, j    , k    ] + \
                      P_p[i    , j + 1, k    ] + \
                      P_p[i    , j - 1, k    ] + \
                      P_p[i    , j    , k + 1] + \
                      P_p[i    , j    , k - 1]
                )
                P[i, j, k] += 4/3 * K2[i, j, k] * s1

                s2 = (P_p[i + 2, j    , k    ] + \
                      P_p[i - 2, j    , k    ] + \
                      P_p[i    , j + 2, k    ] + \
                      P_p[i    , j - 2, k    ] + \
                      P_p[i    , j    , k + 2] + \
                      P_p[i    , j    , k - 2]
                )
                P[i, j, k] -= K2[i, j, k] / 12 * s2

                s3 = ((P_p[i + 1, j    , k    ] - P_p[i-1 , j  , k  ]) - (P_p[i + 2, j, k] - P_p[i - 2, j, k]) / 8) * (ro[i + 1, j, k] - ro[i - 1, j, k])
                s4 = ((P_p[i    , j + 1, k    ] - P_p[i   , j-1, k  ]) - (P_p[i, j + 2, k] - P_p[i, j - 2, k]) / 8) * (ro[i, j + 1, k] - ro[i, j - 1, k])
                s5 = ((P_p[i    , j    , k + 1] - P_p[i-1 , j  , k-1]) - (P_p[i, j, k + 2] - P_p[i, j, k - 2]) / 8) * (ro[i, j, k + 1] - ro[i, j, k - 1])
                P -= K2_3_ro[i, j, k] * s3
                P -= K2_3_ro[i, j, k] * s4
                P -= K2_3_ro[i, j, k] * s5
    return P[2:-2, 2:-2, 2:-2]

def P(P_pp, P_p):
    '''mb work with flat and then reshape in return'''
    S = P_p.shape[0]
    N = P_p.shape[1]

    P = 2 * P_p - P_pp
    Z = 22.5 * P_p
    
    # P_p_flat = P_p.flatten()

    cell_indeces_flat = np.arange(N**3).reshape(N, N, N)[2:-2, 2:-2, 2:-2].flatten().reshape(-1, 1) # vertical vector

    s1_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
    s2_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2]) * 2  # i±2 j±2 k±2 
    s1_values = P_p.flatten()[s1_indexes_flat] # each row contains 6 neighbors of cell 
    s2_values = P_p.flatten()[s2_indexes_flat] # each row contains 6 neighbors of cell 
    s1 = np.sum(s1_values, axis=1) # sum by axis=1 is faster for default order
    s2 = np.sum(s2_values, axis=1)

    Z[2:-2, 2:-2, 2:-2] -=   4 * s1.reshape(N-4, N-4, N-4)
    Z[2:-2, 2:-2, 2:-2] += 1/4 * s2.reshape(N-4, N-4, N-4)

    s3_V_indexes = cell_indeces_flat + np.array([N**2, -N**2, 2*N**2, -2*N**2])
    s3_V_values = P_p.flatten()[s3_V_indexes] * [1, -1, -1/8, -1/8]
    s3_V_sum = np.sum(s3_V_values, axis=1)
    s3_N_indexes = cell_indeces_flat + np.array([N**2, -N**2])
    s3_N_values = ro.flatten()[s3_N_indexes] * [1, -1]
    s3_N_sum = np.sum(s3_N_values, axis=1)
    s3 = (s3_V_sum / s3_N_sum).reshape(N-4, N-4, N-4)

    s4_V_indexes = cell_indeces_flat + np.array([N, -N, 2*N, -2*N])
    s4_V_values = P_p.flatten()[s4_V_indexes] * [1, -1, -1/8, -1/8]
    s4_V_sum = np.sum(s4_V_values, axis=1)
    s4_N_indexes = cell_indeces_flat + np.array([N, -N])
    s4_N_values = ro.flatten()[s4_N_indexes] * [1, -1]
    s4_N_sum = np.sum(s4_N_values, axis=1)
    s4 = (s4_V_sum / s4_N_sum).reshape(N-4, N-4, N-4)

    s5_V_indexes = cell_indeces_flat + np.array([1, -1, 2, -2])
    s5_V_values = P_p.flatten()[s5_V_indexes] * [1, -1, -1/8, -1/8]
    s5_V_sum = np.sum(s5_V_values, axis=1)
    s5_N_indexes = cell_indeces_flat + np.array([N, -N])
    s5_N_values = ro.flatten()[s5_N_indexes] * [1, -1]
    s5_N_sum = np.sum(s5_N_values, axis=1)
    s5 = (s5_V_sum / s5_N_sum).reshape(N-4, N-4, N-4)

    Z[2:-2, 2:-2, 2:-2] += (s3 + s4 + s5) * ro[2:-2, 2:-2, 2:-2]
    P -= Z * K2 / 3

    return P[2:-2, 2:-2, 2:-2]

# P = P(P_pp, P_p)
# print(P.shape)

t0 = time()
P1 = old_slow1(P_pp, P_p)
t_P1 = time() - t0 
print(t_P1)

t0 = time()
P2 = P(P_pp, P_p)
t_P2 = time() - t0
print(t_P2)

print(f't_P1 / t_P2 = {t_P1 / t_P2}')

print(f'np.array_equal(P1, P2)\t{np.array_equal(P1, P2)}')
print(f'np.allclose(P1, P2):\t{np.allclose(P1, P2)}')

print(P1[3,3,3])
print(P2[3,3,3])

print(np.sum(P1) - np.sum(P2))
