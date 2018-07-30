import numpy as np
from time import time
import matplotlib.pyplot as plt
# plt.rcParams['figure.figsize'] = [10, 10] # 10 x 10 inches plot

# r = np.random.random((12, 16, 16))
# r = np.load('../3d_numpy_array_reduced-58-64-64.npy')#[::4,::4,::4]
k = 4
r = np.load('../cube-full-460-512-512.npy')[::k,::k,::k]
# r = np.load('../3d_numpy_array_reduced-58-64-64.npy')
ro  = 1e-5 + 1.24e-3*r - 2.83e-7*r*r + 2.79e-11*r*r*r
c = (ro + 0.112) * 1.38e-6

# тут не факт что все 1
l = 1 # dt
h = 1 # dx = dy = dz
K = l / h * c
K2 = K**2
K_2_by_3 = K**2 / 3
K2_3_ro = K2 / 3 / ro


# initial conditions
# P_pp = np.zeros_like(ro) # previous previous t - 2
# P_p  = np.zeros_like(ro) # previous          t - 1
# P    = np.zeros_like(ro) # current           t


N = 16
S = 16 # first test simple case when N == S
P_pp = np.random.random(ro.shape) # previous previous t - 2
P_p  = np.random.random(ro.shape) # previous          t - 1
P    = np.zeros(ro.shape, dtype=np.float64) # current           t







def old_slow1(P_pp, P_p):
    '''slow explicit n^3, c-style implementation v0.2'''
    
    S = P_p.shape[0]
    N = P_p.shape[1]

    # P[2:-2, 2:-2, 2:-2] = (2 - 7.5 * K2[2:-2, 2:-2, 2:-2]) * P_p[2:-2, 2:-2, 2:-2] - P_pp[2:-2, 2:-2, 2:-2]
    P = np.zeros_like(P_p)

    P[2:-2, 2:-2, 2:-2] = (2 - 7.5 * K2[2:-2, 2:-2, 2:-2]) * P_p[2:-2, 2:-2, 2:-2] - P_pp[2:-2, 2:-2, 2:-2]


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
    P[ro < 0.1] = 0
    return P


def P_step(P_pp, P_p):
    '''
    mb work with flat and then reshape in return
    norm by now, mb add some more optimisations in future, also cuda
    '''

    S = P_p.shape[0]
    N = P_p.shape[1]
    
    P = np.zeros_like(P_p)
    P[2:-2, 2:-2, 2:-2] = 2 * P_p[2:-2, 2:-2, 2:-2] - P_pp[2:-2, 2:-2, 2:-2]
    Z = np.zeros_like(P_p)
    Z[2:-2, 2:-2, 2:-2] = 22.5 * P_p[2:-2, 2:-2, 2:-2]
    
    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police1: {bound_sum}')

    cell_indeces_flat = np.arange(S * N * N).reshape(S, N, N)[2:-2, 2:-2, 2:-2].flatten().reshape(-1, 1) # vertical vector

    s1_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
    s2_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2]) * 2  # i±2 j±2 k±2 
    s1_values = P_p.flatten()[s1_indexes_flat] # each row contains 6 neighbors of cell 
    s2_values = P_p.flatten()[s2_indexes_flat] # each row contains 6 neighbors of cell 
    s1 = np.sum(s1_values, axis=1) # sum by axis=1 is faster for default order
    s2 = np.sum(s2_values, axis=1)

    Z[2:-2, 2:-2, 2:-2] -=   4 * s1.reshape(S-4, N-4, N-4)
    Z[2:-2, 2:-2, 2:-2] += 1/4 * s2.reshape(S-4, N-4, N-4)

    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police2: {bound_sum}')

    m1 = np.array([1, -1, -1/8, -1/8])
    m2 = np.array([1, -1])

    s3_V_indexes = cell_indeces_flat + np.array([N**2, -N**2, 2*N**2, -2*N**2])
    s3_V_values = P_p.flatten()[s3_V_indexes] * m1 # po idee mozhno za skobki kak to vinesti m1 i m2
    # print(P_p.max())
    s3_V_sum = np.sum(s3_V_values, axis=1)
    s3_N_indexes = cell_indeces_flat + np.array([N**2, -N**2])
    s3_N_values = ro.flatten()[s3_N_indexes] * m2
    s3_N_sum = np.sum(s3_N_values, axis=1)
    s3 = (s3_V_sum * s3_N_sum).reshape(S-4, N-4, N-4)
    # print(s3_V_sum.max(), s3_V_sum.min())
    # print(len(s3_N_sum) ,len(s3_N_sum == 0))
    # print(s3_N_sum.max(), s3_N_sum.min(), len(s3_N_sum == 0))
    #     print(s3_V_sum)
    
    s4_V_indexes = cell_indeces_flat + np.array([N, -N, 2*N, -2*N])
    s4_V_values = P_p.flatten()[s4_V_indexes] * m1
    s4_V_sum = np.sum(s4_V_values, axis=1)
    s4_N_indexes = cell_indeces_flat + np.array([N, -N])
    s4_N_values = ro.flatten()[s4_N_indexes] * m2
    s4_N_sum = np.sum(s4_N_values, axis=1)
    s4 = (s4_V_sum * s4_N_sum).reshape(S-4, N-4, N-4)
    #     print(s4_V_sum.max(), s4_V_sum.min())

    s5_V_indexes = cell_indeces_flat + np.array([1, -1, 2, -2])
    s5_V_values = P_p.flatten()[s5_V_indexes] * m1
    s5_V_sum = np.sum(s5_V_values, axis=1)
    s5_N_indexes = cell_indeces_flat + np.array([1, -1])
    s5_N_values = ro.flatten()[s5_N_indexes] * m2
    s5_N_sum = np.sum(s5_N_values, axis=1)
    s5 = (s5_V_sum * s5_N_sum).reshape(S-4, N-4, N-4)
    #     print(s5_V_sum.max(), s5_V_sum.min())
    
    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police3: {bound_sum}')

    Z[2:-2, 2:-2, 2:-2] += (s3 + s4 + s5) * ro[2:-2, 2:-2, 2:-2]
    
    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police4: {bound_sum}')
    
    P[2:-2, 2:-2, 2:-2] -= Z[2:-2, 2:-2, 2:-2] * K_2_by_3[2:-2, 2:-2, 2:-2]
    #     P -= Z * K_2_by_3

    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police5: {bound_sum}')

    P[ro < 0.1] = 0
    
    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police0: {bound_sum}')
    #     return P[2:-2, 2:-2, 2:-2] # should return array of shape (S, N, N)
    #     print(np.mean(P))
    #     print(f'bug police4: {np.sum(P[:2])}') # for some reason outside boundaries != 0. P_step() should affect only inner slice of array [2:-2, 2:-2, 2:-2]
    return P

def P_step_ravel(P_pp, P_p):
    '''
    mb work with flat and then reshape in return
    norm by now, mb add some more optimisations in future, also cuda
    '''

    S = P_p.shape[0]
    N = P_p.shape[1]
    
    P = np.zeros_like(P_p)
    P[2:-2, 2:-2, 2:-2] = 2 * P_p[2:-2, 2:-2, 2:-2] - P_pp[2:-2, 2:-2, 2:-2]
    Z = np.zeros_like(P_p)
    Z[2:-2, 2:-2, 2:-2] = 22.5 * P_p[2:-2, 2:-2, 2:-2]
    
    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police1: {bound_sum}')

    cell_indeces_flat = np.arange(S * N * N).reshape(S, N, N)[2:-2, 2:-2, 2:-2].ravel().reshape(-1, 1) # vertical vector

    s1_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
    s2_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2]) * 2  # i±2 j±2 k±2 
    s1_values = P_p.ravel()[s1_indexes_flat] # each row contains 6 neighbors of cell 
    s2_values = P_p.ravel()[s2_indexes_flat] # each row contains 6 neighbors of cell 
    s1 = np.sum(s1_values, axis=1) # sum by axis=1 is faster for default order
    s2 = np.sum(s2_values, axis=1)

    Z[2:-2, 2:-2, 2:-2] -=   4 * s1.reshape(S-4, N-4, N-4)
    Z[2:-2, 2:-2, 2:-2] += 1/4 * s2.reshape(S-4, N-4, N-4)

    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police2: {bound_sum}')

    m1 = np.array([1, -1, -1/8, -1/8])
    m2 = np.array([1, -1])

    s3_V_indexes = cell_indeces_flat + np.array([N**2, -N**2, 2*N**2, -2*N**2])
    s3_V_values = P_p.ravel()[s3_V_indexes] * m1 # po idee mozhno za skobki kak to vinesti m1 i m2
    # print(P_p.max())
    s3_V_sum = np.sum(s3_V_values, axis=1)
    s3_N_indexes = cell_indeces_flat + np.array([N**2, -N**2])
    s3_N_values = ro.ravel()[s3_N_indexes] * m2
    s3_N_sum = np.sum(s3_N_values, axis=1)
    s3 = (s3_V_sum * s3_N_sum).reshape(S-4, N-4, N-4)
    # print(s3_V_sum.max(), s3_V_sum.min())
    # print(len(s3_N_sum) ,len(s3_N_sum == 0))
    # print(s3_N_sum.max(), s3_N_sum.min(), len(s3_N_sum == 0))
    #     print(s3_V_sum)
    
    s4_V_indexes = cell_indeces_flat + np.array([N, -N, 2*N, -2*N])
    s4_V_values = P_p.ravel()[s4_V_indexes] * m1
    s4_V_sum = np.sum(s4_V_values, axis=1)
    s4_N_indexes = cell_indeces_flat + np.array([N, -N])
    s4_N_values = ro.ravel()[s4_N_indexes] * m2
    s4_N_sum = np.sum(s4_N_values, axis=1)
    s4 = (s4_V_sum * s4_N_sum).reshape(S-4, N-4, N-4)
    #     print(s4_V_sum.max(), s4_V_sum.min())

    s5_V_indexes = cell_indeces_flat + np.array([1, -1, 2, -2])
    s5_V_values = P_p.ravel()[s5_V_indexes] * m1
    s5_V_sum = np.sum(s5_V_values, axis=1)
    s5_N_indexes = cell_indeces_flat + np.array([1, -1])
    s5_N_values = ro.ravel()[s5_N_indexes] * m2
    s5_N_sum = np.sum(s5_N_values, axis=1)
    s5 = (s5_V_sum * s5_N_sum).reshape(S-4, N-4, N-4)
    #     print(s5_V_sum.max(), s5_V_sum.min())
    
    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police3: {bound_sum}')

    Z[2:-2, 2:-2, 2:-2] += (s3 + s4 + s5) * ro[2:-2, 2:-2, 2:-2]
    
    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police4: {bound_sum}')
    
    P[2:-2, 2:-2, 2:-2] -= Z[2:-2, 2:-2, 2:-2] * K_2_by_3[2:-2, 2:-2, 2:-2]
    #     P -= Z * K_2_by_3

    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police5: {bound_sum}')

    P[ro < 0.1] = 0
    
    bound_sum = np.sum(P[:2])
    if(bound_sum != 0):
        print(f'bug police0: {bound_sum}')
    #     return P[2:-2, 2:-2, 2:-2] # should return array of shape (S, N, N)
    #     print(np.mean(P))
    #     print(f'bug police4: {np.sum(P[:2])}') # for some reason outside boundaries != 0. P_step() should affect only inner slice of array [2:-2, 2:-2, 2:-2]
    return P


LOOPS = 1

t0 = time()
for i in range(LOOPS):
    a1 = P_step(P_pp, P_p)
print(time() - t0)

t0 = time()
for i in range(LOOPS):
    a2 = P_step_ravel(P_pp, P_p)
print(time() - t0)

# print(alpha_2)
print(np.allclose(a1, a2))
print(a1[30, 30, 30])
print(a2[30, 30, 30])
# print(np.mean(alpha_1), np.mean(alpha_2), np.max(alpha_2))
