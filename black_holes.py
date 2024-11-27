import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from matplotlib.animation import FuncAnimation

# Constants
G = 1.0 
M = 1.0   
c = 1.0   
vx = 0.5   

# Function for the Lorentz Factor (gamma)
gamma = 1 / np.sqrt(1 - vx**2)

# Geodesic Equation (with the Boost Correction)
def geodesic_equation(state, tau):
    r, theta, phi, dr_dt, dtheta_dt, dphi_dt = state
    x = r * np.sin(theta) * np.cos(phi)  

    d2r_dt2 = -G * M / r**2 / (1 + gamma**2 * (x * vx / r)**2) - 0.01 * dr_dt**2
    d2theta_dt2 = (dphi_dt**2) * np.cos(theta) / np.sin(theta)  
    d2phi_dt2 = 0  

    return [dr_dt, dtheta_dt, dphi_dt, d2r_dt2, d2theta_dt2, d2phi_dt2]

# Initial Conditions
r0 = 10.0
theta0 = np.pi / 2
phi0 = 0.0
dr_dt0 = -0.1
dtheta_dt0 = 0.0
dphi_dt0 = 0.8

# Time
tau = np.linspace(0, 200, 1000)

state0 = [r0, theta0, phi0, dr_dt0, dtheta_dt0, dphi_dt0]
solution = odeint(geodesic_equation, state0, tau)

r = solution[:, 0]
phi = solution[:, 2]

# Create a graphic
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
ax.set_title('Spiral Orbit Around a Moving Black Hole')

# Initial Orbit Configuration
line, = ax.plot([], [], label="Object's Orbit")
ax.set_ylim(0, np.max(r))

# Function for animation
def init():
    line.set_data([], [])
    return line,

def update(frame):
    line.set_data(phi[:frame], r[:frame])
    return line,

ani = FuncAnimation(fig, update, frames=len(tau), init_func=init, blit=True, interval=1)

plt.legend()
plt.show()
