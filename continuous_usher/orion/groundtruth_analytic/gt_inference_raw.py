import sys
import numpy as np
from math import pi,sin,cos
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from GT_data_utils import loadDFfromFiles

#state_files = ['../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-36-33.txt',
#               '../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-41-02.txt',
#               '../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-42-19.txt',
#               '../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-49-16.txt',
#               '../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-51-43.txt',
#               '../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-52-43.txt']
#
#control_signal_files = ['../real_robot_data/Jan10_2020_Control_Signals/control_take1.csg',
#                        '../real_robot_data/Jan10_2020_Control_Signals/control_take2.csg',
#                        '../real_robot_data/Jan10_2020_Control_Signals/control_take3.csg',
#                        '../real_robot_data/Jan10_2020_Control_Signals/control_take5.csg',
#                        '../real_robot_data/Jan10_2020_Control_Signals/control_take6.csg',
#                        '../real_robot_data/Jan10_2020_Control_Signals/control_take7.csg']

#state_files = ['../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-36-33.txt',
#               '../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-42-19.txt',
#               '../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-49-16.txt',]
#
#control_signal_files = ['../real_robot_data/Jan10_2020_Control_Signals/control_take1.csg',
#                        '../real_robot_data/Jan10_2020_Control_Signals/control_take3.csg',
#                        '../real_robot_data/Jan10_2020_Control_Signals/control_take5.csg',]

state_files = ['../camera_calibration/outputs/fixed_dat_info/2020-01-10_15-49-16.txt',]

control_signal_files = ['../real_robot_data/Jan10_2020_Control_Signals/control_take5.csg',]

motor_rpm = (330.*2.*pi)/60.
mass = 4.
gravity = 9.8
radius = .03
stall_torque = .6
dt = .01
la = .11
lb = .1
signs = np.array([1.,-1.,-1.,1.])
np.random.seed(7)

def desired_angular_velocity(signal):
    return (signal/255.)*motor_rpm

def compute_omega(mu,desired_velocity):
    return desired_velocity*(1. - (mu * mass * gravity * radius)/(4. * stall_torque))

def derivative_omega(desired_velocity):
    return -(desired_velocity * mass * gravity * radius)/(4. * stall_torque)

def compute_matrix():
    scale = 1./radius
    return np.matrix([[-1.,1.,la+lb],[1.,1.,-(la+lb)],[-1.,1.,-(la+lb)],[1.,1.,(la+lb)]]) * scale

# compute pseudo-inverse of transformation matrix
A = np.linalg.pinv(compute_matrix())

def compute_velocity(mu,control_signals):
    # compute omega
    desired_velocity = desired_angular_velocity(control_signals*signs)
    omega = compute_omega(mu,desired_velocity)

    # compute linear and angular velocities
    x = A.dot(omega)
    return np.squeeze(np.asarray(x))

def read_control_signals(filename):
    time = []
    control_signals = []
    with open(filename,'r') as f:
        for idx,line in enumerate(f.readlines()):
            line = line.rstrip('\n')
            values = [float(i) for i in line.split(' ')]
            time.append(np.array([values[0]]))
            control_signals.append(np.array([values[3],values[4],values[2],values[1]]))
    return time,control_signals

def read_state_info(dat):
    x = dat['pose_t_x'].to_numpy()
    y = dat['pose_t_y'].to_numpy()
    orn = dat['q_angle'].to_numpy()

    pos = []
    for i in range(len(x)):
        pos.append([x[i],y[i],(pi/180.)*orn[i]])
    return pos

print("Reading ground truth data and control signals...")
time = []
control_signals = []
pos_gt = []
for idx,csf in enumerate(control_signal_files):
    t,cs = read_control_signals(csf)
    dat_gt = loadDFfromFiles(state_files[idx])
    pos = read_state_info(dat_gt)
    time.append(t)
    control_signals.append(cs)
    pos_gt.append(pos)
print("Data read successfully.")

def compute_bounding_box(poses):
    xmin = 1e10
    xmax = -1e10
    ymin = 1e10
    ymax = -1e10

    for pos in poses:
        for p in pos:
            xmin = min(xmin,p[0])
            xmax = max(xmax,p[0])
            ymin = min(ymin,p[1])
            ymax = max(ymax,p[1])
    return xmin,xmax,ymin,ymax

def draw_trajectories(poses,colors,symbols,labels):
    xmin,xmax,ymin,ymax = compute_bounding_box(poses)
    x_length = abs(xmax - xmin)
    y_length = abs(ymin - ymax)
    if(x_length < .3*y_length): x_length = y_length

    plt.cla()
    plt.gca().set_xlim([xmin - np.sign(xmax)*.05*x_length, xmin + np.sign(xmax)*(x_length + .05)])
    plt.gca().set_ylim([ymin - np.sign(ymax)*.05*y_length, ymin + np.sign(ymax)*(y_length + .05)])

    for idx,pos in enumerate(poses):
        x = []
        y = []
        for p in pos:
            x.append(p[0])
            y.append(p[1])
        plt.plot(x,y,symbols[idx],color=colors[idx],label=labels[idx],linewidth=2)

    plt.legend()
    plt.show()

def compute_trajectory(friction,idx):
    pos = []
    dt = time[idx][1]-time[idx][0]

    n_traj = int(len(pos_gt[idx]))
    n_sim = len(time[idx])

    index_before_mapping = list(range(n_traj))
    index_after_mapping = [int(round(x/(n_traj-1)*(n_sim-1))) for x in index_before_mapping]

    gt_mapping = np.zeros(n_sim)
    for i in index_after_mapping:
        gt_mapping[i] = 1.

    current_pos = pos_gt[idx][0]
    for i in range(len(time[idx])):
        if(gt_mapping[i]==1.): pos.append(current_pos)
        orn = current_pos[2]
        x = compute_velocity(friction,control_signals[idx][i])
        B = np.matrix([[cos(orn),-sin(orn),0.],[sin(orn),cos(orn),0.],[0.,0.,1.]])
        vel = B.dot(x)
        vel = np.squeeze(np.asarray(vel))
        x_pos = current_pos[0] + dt*vel[0]
        y_pos = current_pos[1] + dt*vel[1]
        orn = current_pos[2] + dt*vel[2]
        current_pos = [x_pos,y_pos,orn]

    return pos

def loss(friction):
    # check if any coefficient is negative, and penalize heavily in that case.
    is_invalid = False
    for i in range(4):
        if(friction[i] < 0.): is_invalid = True
    if(is_invalid): return np.inf

    value = 0.
    for idx,p in enumerate(pos_gt):
        pos = compute_trajectory(friction,idx)
        for i in range(len(pos_gt[idx])):
            value += np.sqrt((p[i][0] - pos[i][0])**2 + (p[i][1] - pos[i][1])**2 + (p[i][2] - pos[i][2])**2)
    return value

def loss_derivative(friction):
    grad = np.zeros(4)
    for idx,p in enumerate(pos_gt):
        J = np.zeros((3,4))
        dt = time[idx][1]-time[idx][0]

        n_traj = int(len(pos_gt[idx]))
        n_sim = len(time[idx])

        index_before_mapping = list(range(n_traj))
        index_after_mapping = [int(round(x/(n_traj-1)*(n_sim-1))) for x in index_before_mapping]

        gt_mapping = np.zeros(n_sim)
        for t,i in enumerate(index_after_mapping):
            gt_mapping[i] = index_before_mapping[t]

        current_pos = pos_gt[idx][0]
        for i in range(1,len(time[idx])):
            x = compute_velocity(friction,control_signals[idx][i])
            d_omega = derivative_omega(desired_angular_velocity(control_signals[idx][i]*signs))
            orn = current_pos[2]

            for j in range(4):
                J[0,j] += dt*(cos(orn) - sin(orn))*A[0,j]*d_omega[j] - dt*(x[0]*sin(orn) + x[1]*cos(orn))*J[2,j]
                J[1,j] += dt*(sin(orn) + cos(orn))*A[1,j]*d_omega[j] + dt*(x[0]*cos(orn) - x[1]*sin(orn))*J[2,j]
                J[2,j] += dt*A[2,j]*d_omega[j]

            if(gt_mapping[i]!=0.):
                point = p[int(gt_mapping[i])]
                pos_diff = np.array([current_pos[0]-point[0],current_pos[1]-point[1],current_pos[2]-point[2]])
                distance = max(1e-16,np.sqrt(pos_diff[0]**2 + pos_diff[1]**2 + pos_diff[2]**2))
                current_grad = J.transpose().dot(pos_diff)
                current_grad = np.squeeze(np.asarray(current_grad))
                grad += (1./distance) * current_grad

            B = np.matrix([[cos(orn),-sin(orn),0.],[sin(orn),cos(orn),0.],[0.,0.,1.]])
            vel = B.dot(x)
            vel = np.squeeze(np.asarray(vel))
            x_pos = current_pos[0] + dt*vel[0]
            y_pos = current_pos[1] + dt*vel[1]
            orn = current_pos[2] + dt*vel[2]
            current_pos = [x_pos,y_pos,orn]
    return grad

def main():
    mu0 = np.random.rand(4)
    print('Initial Guess: ',mu0)
    print('Initial Loss: ',loss(mu0))
    # res = minimize(loss,mu0,method='nelder-mead',options={'disp': True})
    res = minimize(loss,mu0,method='BFGS',jac=loss_derivative,options={'disp': True})
    print('Final coefficients: ',res.x)
    print(loss(res.x))

    for idx,p in enumerate(pos_gt):
        poses = []
        colors = []
        symbols = []
        labels = []
        poses.append(p)
        colors.append('b')
        symbols.append('go--')
        labels.append('Ground Truth')

        pos = compute_trajectory(res.x,idx)
        poses.append(pos)
        colors.append('r')
        symbols.append('.')
        labels.append('Prediction')
        
        draw_trajectories(poses,colors,symbols,labels)

if __name__ == '__main__':
    main()
