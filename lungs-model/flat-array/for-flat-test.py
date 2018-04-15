# This code compares triple-for loop and flat von neimann neighbours implementations
# and tests if this 2 methods gives the same result
# also test that 460 instead of 512 on 0-axis

# firstly i remove this condition:
            # if ro[i, j, k] < 0.1 and i != A and j != B and k != C: # refl􏰂ecting condition | use numpy masking
                # P[i, j, k] = 0

import numpy as np

N = 16
# S = 10 # number of slices / CT-images / scans
S = 16 # first test simple case when N == S

# r = np.random.random((S, N, N))
r = np.load('r.npy')
ro  = 1e-5 + 1.24e-3*r - 2.83e-7*r*r + 2.79e-11*r*r*r
# c = np.empty_like(r)
c = (ro + 0.112) * 1.38e-6

# тут не факт что все 1
l = 1 # dt
h = 1 # dx = dy = dz

K = l / h * c
K2 = K**2
K2_3_ro = K2 / 3 / ro


# initial conditions
# P_pp = np.random.random((S, N, N)) # previous previous t - 2
# P_p  = np.random.random((S, N, N)) # previous          t - 1

P_pp = np.load('P_pp.npy')
P_p = np.load('P_p.npy')
# P    = np.zeros((S, N, N), dtype=np.float64) # current           t

# np.save('P_pp.npy', P_pp)
# np.save('P_p.npy', P_p)
# np.save('r.npy', r)

def old_slow0(P_pp, P_p):
    '''slow explicit n^3, c-style implementation v0.2'''
    
    S = P_p.shape[0]
    N = P_p.shape[1]
    P = np.zeros((S, N, N)) 


    for i in range(2, S - 2):
        for j in range(2, N - 2):
            for k in range(2, N - 2):


                # need some optimisation, with K2, K2_3_ro, чтобы считать меньше
                # K2. K2_3_ro - put outside for loops
                # Первое слагаемое можно тоже вынести outside for loops - там простое сложение
                # можно slices + sum вместо много + + + +
                P[i, j, k] = (2 - 7.5 * K2[i, j, k]) * P_p[i, j, k] - P_pp[i, j, k] \
                    # + 4/3 * K2[i, j, k] * (P_p[i + 1, j    , k    ] + \
                    #               P_p[i - 1, j    , k    ] + \
                    #               P_p[i    , j + 1, k    ] + \
                    #               P_p[i    , j - 1, k    ] + \
                    #               P_p[i    , j    , k + 1] + \
                    #               P_p[i    , j    , k - 1] ) \
                    # - K2[i, j, k] / 12 *  (P_p[i + 2, j    , k    ] + \
                    #               P_p[i - 2, j    , k    ] + \
                    #               P_p[i    , j + 2, k    ] + \
                    #               P_p[i    , j - 2, k    ] + \
                    #               P_p[i    , j    , k + 2] + \
                    #               P_p[i    , j    , k - 2] ) \
                    # - K2_3_ro[i, j, k] * ((P_p[i + 1, j    , k    ] - P_p[i-1 , j  , k  ]) - (P_p[i + 2, j, k] - P_p[i - 2, j, k]) / 8) * (ro[i + 1, j, k] - ro[i - 1, j, k]) \
                    # - K2_3_ro[i, j, k] * ((P_p[i    , j + 1, k    ] - P_p[i   , j-1, k  ]) - (P_p[i, j + 2, k] - P_p[i, j - 2, k]) / 8) * (ro[i, j + 1, k] - ro[i, j - 1, k]) \
                    # - K2_3_ro[i, j, k] * ((P_p[i    , j    , k + 1] - P_p[i-1 , j  , k-1]) - (P_p[i, j, k + 2] - P_p[i, j, k - 2]) / 8) * (ro[i, j, k + 1] - ro[i, j, k - 1])
    return P[2:-2, 2:-2, 2:-2]

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


                # need some optimisation, with K2, K2_3_ro, чтобы считать меньше
                # K2. K2_3_ro - put outside for loops
                # Первое слагаемое можно тоже вынести outside for loops - там простое сложение
                # можно slices + sum вместо много + + + +


                s1 = (P_p[i + 1, j    , k    ] + \
                      P_p[i - 1, j    , k    ] + \
                      P_p[i    , j + 1, k    ] + \
                      P_p[i    , j - 1, k    ] + \
                      P_p[i    , j    , k + 1] + \
                      P_p[i    , j    , k - 1]
                )
                P[i, j, k] += 4/3 * K2[i, j, k] * s1

                # s2 = (P_p[i + 2, j    , k    ] + \
                #       P_p[i - 2, j    , k    ] + \
                #       P_p[i    , j + 2, k    ] + \
                #       P_p[i    , j - 2, k    ] + \
                #       P_p[i    , j    , k + 2] + \
                #       P_p[i    , j    , k - 2]
                # )
                # P[i, j, k] -= K2[i, j, k] / 12 * s2

                # s3 = ((P_p[i + 1, j    , k    ] - P_p[i-1 , j  , k  ]) - (P_p[i + 2, j, k] - P_p[i - 2, j, k]) / 8) * (ro[i + 1, j, k] - ro[i - 1, j, k])
                # s4 = ((P_p[i    , j + 1, k    ] - P_p[i   , j-1, k  ]) - (P_p[i, j + 2, k] - P_p[i, j - 2, k]) / 8) * (ro[i, j + 1, k] - ro[i, j - 1, k])
                # s5 = ((P_p[i    , j    , k + 1] - P_p[i-1 , j  , k-1]) - (P_p[i, j, k + 2] - P_p[i, j, k - 2]) / 8) * (ro[i, j, k + 1] - ro[i, j, k - 1])
                # P -= K2_3_ro[i, j, k] * s3
                # P -= K2_3_ro[i, j, k] * s4
                # P -= K2_3_ro[i, j, k] * s5
    return P[2:-2, 2:-2, 2:-2]

def old_slow2(P_pp, P_p):
    '''slow explicit n^3, c-style implementation v0.2'''
    
    S = P_p.shape[0]
    N = P_p.shape[1]

    # P[2:-2, 2:-2, 2:-2] = (2 - 7.5 * K2[2:-2, 2:-2, 2:-2]) * P_p[2:-2, 2:-2, 2:-2] - P_pp[2:-2, 2:-2, 2:-2]
    # P = np.zeros_like(P_p)
    P = (2 - 7.5 * K2) * P_p - P_pp
    
    # P_p_flat = P_p.flatten()

    cell_indeces_flat = np.arange(N**3).reshape(N, N, N)[1:-1, 1:-1, 1:-1].flatten().reshape(-1, 1) # vertical vector
    neighbours1_indeces_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
    neighbours_cell_all = P_p.flatten()[neighbours1_indeces_flat] # each row contains 6 neighbors of cell 
    neighbours_cell_all_sum = np.sum(neighbours_cell_all, axis=1)
    P[1:-1, 1:-1, 1:-1] += 4/3 * K2[1:-1, 1:-1, 1:-1] * (P.flatten()[cell_indeces_flat.reshape(-1)] + neighbours_cell_all_sum).reshape(N-2, N-2, N-2)


    # cell_indeces_flat = np.arange(N**3).reshape(N, N, N)[2:-2, 2:-2, 2:-2].flatten().reshape(-1, 1) # vertical vector
    # neighbours1 = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
    # neighbours2 = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2]) * 2  # i±2 j±2 k±2 

    # print('sum:', np.sum(P[neighbours1], axis=1)[0])
    # BUG: allclose == true, even if you comment next 2 lines
    # P[2:-2, 2:-2, 2:-2] += 4 /  3 * K2[2:-2, 2:-2, 2:-2] * np.sum(P.flatten()[neighbours1], axis=1).reshape(N - 4, N - 4, N - 4)
    # P[2:-2, 2:-2, 2:-2] -= 1 / 12 * K2[2:-2, 2:-2, 2:-2] * np.sum(neighbours2, axis=1).reshape(N - 4, N - 4, N - 4)

    # for i in range(2, S - 2):
    #     for j in range(2, N - 2):
    #         for k in range(2, N - 2):


                # need some optimisation, with K2, K2_3_ro, чтобы считать меньше
                # K2. K2_3_ro - put outside for loops
                # Первое слагаемое можно тоже вынести outside for loops - там простое сложение
                # можно slices + sum вместо много + + + +


                # s1 = (P_p[i + 1, j    , k    ] + \
                      # P_p[i - 1, j    , k    ] + \
                      # P_p[i    , j + 1, k    ] + \
                      # P_p[i    , j - 1, k    ] + \
                      # P_p[i    , j    , k + 1] + \
                      # P_p[i    , j    , k - 1]
                # )
                # P[i, j, k] += 4/3 * K2[i, j, k] * s1

                # s2 = (P_p[i + 2, j    , k    ] + \
                #       P_p[i - 2, j    , k    ] + \
                #       P_p[i    , j + 2, k    ] + \
                #       P_p[i    , j - 2, k    ] + \
                #       P_p[i    , j    , k + 2] + \
                #       P_p[i    , j    , k - 2]
                # )
                # P[i, j, k] -= K2[i, j, k] / 12 * s2

                # s3 = ((P_p[i + 1, j    , k    ] - P_p[i-1 , j  , k  ]) - (P_p[i + 2, j, k] - P_p[i - 2, j, k]) / 8) * (ro[i + 1, j, k] - ro[i - 1, j, k])
                # s4 = ((P_p[i    , j + 1, k    ] - P_p[i   , j-1, k  ]) - (P_p[i, j + 2, k] - P_p[i, j - 2, k]) / 8) * (ro[i, j + 1, k] - ro[i, j - 1, k])
                # s5 = ((P_p[i    , j    , k + 1] - P_p[i-1 , j  , k-1]) - (P_p[i, j, k + 2] - P_p[i, j, k - 2]) / 8) * (ro[i, j, k + 1] - ro[i, j, k - 1])
                # P -= K2_3_ro[i, j, k] * s3
                # P -= K2_3_ro[i, j, k] * s4
                # P -= K2_3_ro[i, j, k] * s5
    return P[2:-2, 2:-2, 2:-2]


P1 = old_slow1(P_pp, P_p)
P2 = old_slow2(P_pp, P_p)
print(f'np.array_equal(P1, P2)\t{np.array_equal(P1, P2)}')
print(f'np.allclose(P1, P2):\t{np.allclose(P1, P2)}')
# print(np.equal(P1, P2))
# print(np.equal(P1[:2,:2,:2], P2[:2,:2,:2]))
# print(P1[:2,:2,:2])
# print(P2[:2,:2,:2])
# print(P1.dtype)
# print(P2.dtype)

print(P1[0,0,0])
print(P2[0,0,0])

print(f'delta = {abs(P1[0,0,0] - P2[0,0,0])}')
