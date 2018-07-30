import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

r = np.load('../3d_numpy_array_reduced-58-64-64.npy')
ro  = 1e-5 + 1.24e-3*r - 2.83e-7*r*r + 2.79e-11*r*r*r
c = (ro + 0.112) * 1.38e-6


t = 0
l = 0.1 # dt, time step
h = 1 # dx = dy = dz = 1mm
K = l / h * c
K2 = K**2
K_2_by_3 = K**2 / 3

# initial conditions
P_pp = np.zeros_like(ro) # previous previous t - 2
P_p  = np.zeros_like(ro) # previous          t - 1
P    = np.zeros_like(ro) # current           t

rows = 8
cols = 4

fig, ax = plt.subplots(rows, cols, figsize=(8,8))
def draw_slices(cube, title_text=0):
    k = 0
    for row in range(rows):
        for col in range(cols):
            ax[row, col].set_title(f'slice {k}')
            ax[row, col].imshow(cube[k], cmap='viridis')
            ax[row, col].axis('off')
            k += 1

    # you can adjust it from plt.show() dialog
    plt.subplots_adjust(wspace=0, hspace=0.3)
    plt.subplots_adjust(left=0, right=1, top=0.9, bottom=0)
    plt.suptitle(title_text)
    # plt.show()
    plt.draw()

draw_slices(P)


def p_step():
    global P
    '''
    mb work with flat and then reshape in return
    norm by now, mb add some more optimisations in future, also cuda
    '''

    S = P_p.shape[0]
    N = P_p.shape[1]

    P[2:-2, 2:-2, 2:-2] = 2 * P_p[2:-2, 2:-2, 2:-2] - P_pp[2:-2, 2:-2, 2:-2]

    Z = np.zeros_like(P_p)
    Z[2:-2, 2:-2, 2:-2] = 22.5 * P_p[2:-2, 2:-2, 2:-2]
    
    cell_indeces_flat = np.arange(S * N * N).reshape(S, N, N)[2:-2, 2:-2, 2:-2].flatten().reshape(-1, 1) # vertical vector

    s1_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2])      # i±1 j±1 k±1 
    s2_indexes_flat = cell_indeces_flat + np.array([-1, 1, -N, N, -N**2, N**2]) * 2  # i±2 j±2 k±2 
    s1_values = P_p.flatten()[s1_indexes_flat] # each row contains 6 neighbors of cell 
    s2_values = P_p.flatten()[s2_indexes_flat] # each row contains 6 neighbors of cell 
    s1 = np.sum(s1_values, axis=1) # sum by axis=1 is faster for default order
    s2 = np.sum(s2_values, axis=1)

    Z[2:-2, 2:-2, 2:-2] -=   4 * s1.reshape(S-4, N-4, N-4)
    Z[2:-2, 2:-2, 2:-2] += 1/4 * s2.reshape(S-4, N-4, N-4)

    m1 = np.array([1, -1, -1/8, -1/8])
    m2 = np.array([1, -1])

    s3_V_indexes = cell_indeces_flat + np.array([N**2, -N**2, 2*N**2, -2*N**2])
    s3_V_values = P_p.flatten()[s3_V_indexes] * m1 # po idee mozhno za skobki kak to vinesti m1 i m2
    s3_V_sum = np.sum(s3_V_values, axis=1)
    s3_N_indexes = cell_indeces_flat + np.array([N**2, -N**2])
    s3_N_values = ro.flatten()[s3_N_indexes] * m2
    s3_N_sum = np.sum(s3_N_values, axis=1)
    s3 = (s3_V_sum * s3_N_sum).reshape(S-4, N-4, N-4)
    
    s4_V_indexes = cell_indeces_flat + np.array([N, -N, 2*N, -2*N])
    s4_V_values = P_p.flatten()[s4_V_indexes] * m1
    s4_V_sum = np.sum(s4_V_values, axis=1)
    s4_N_indexes = cell_indeces_flat + np.array([N, -N])
    s4_N_values = ro.flatten()[s4_N_indexes] * m2
    s4_N_sum = np.sum(s4_N_values, axis=1)
    s4 = (s4_V_sum * s4_N_sum).reshape(S-4, N-4, N-4)

    s5_V_indexes = cell_indeces_flat + np.array([1, -1, 2, -2])
    s5_V_values = P_p.flatten()[s5_V_indexes] * m1
    s5_V_sum = np.sum(s5_V_values, axis=1)
    s5_N_indexes = cell_indeces_flat + np.array([1, -1])
    s5_N_values = ro.flatten()[s5_N_indexes] * m2
    s5_N_sum = np.sum(s5_N_values, axis=1)
    s5 = (s5_V_sum * s5_N_sum).reshape(S-4, N-4, N-4)

    Z[2:-2, 2:-2, 2:-2] += (s3 + s4 + s5) * ro[2:-2, 2:-2, 2:-2]
    P[2:-2, 2:-2, 2:-2] -= Z[2:-2, 2:-2, 2:-2] * K_2_by_3[2:-2, 2:-2, 2:-2]
    P[ro < 0.1] = 0
    


# cube_slices(P, rows=4, cols=4)


# fig, ax = plt.subplots()

# ax.imshow(P[7])

N = P.shape[1]
A, B, C = 2, N//2, N//2 # sound source location
t = 0
f = 400


def step(event):
    global t, P, P_p, P_pp

    P_old = P
    p_step()
    P[A, B, C] = np.sin(2 * np.pi * f * t)
    P_pp  = P_p
    P_p   = P_old
    t += l

    draw_slices(P, f'pressure at time {t}')


    # plt.savefig('slices.png')
    # plt.savefig('slices.pdf')


    # ax.imshow(P[7])
    # plt.draw()
    print('step')


step_ax = plt.axes([0.7, 0.05, 0.1, 0.075]) # rect = [left, bottom, width, height]
bnext = Button(step_ax, 'Step')
bnext.on_clicked(step)

plt.show()
