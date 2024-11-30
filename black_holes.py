import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from matplotlib.animation import FuncAnimation

# Constants (adjusted)
G = 1.0    
M = 2.0    # Reduced mass
c = 1.0   

# Modified Geodesic Equation with controlled energy loss
def geodesic_equation(state, t):
    r, theta, phi, dr_dt, dtheta_dt, dphi_dt = state
    
    # Gentler dissipation with safety checks
    dissipation = 0.05 * (1.0 + 1.0/(r + 0.1))  # Added small constant to avoid division by zero
    
    # Safer equations with bounded terms
    d2r_dt2 = max(-100, min(100, -G * M / (r**2 + 0.1) - dissipation * dr_dt))
    d2theta_dt2 = 0
    d2phi_dt2 = max(-100, min(100, -dissipation * dphi_dt))

    derivatives = [
        dr_dt,
        dtheta_dt,
        dphi_dt,
        d2r_dt2,
        d2theta_dt2,
        d2phi_dt2
    ]
    return derivatives

# Initial Conditions
r0 = 8.0           # Starting radius
theta0 = np.pi / 2  # Equatorial plane
phi0 = 0.0         # Starting angle
dr_dt0 = -0.05     # Smaller initial inward velocity
dtheta_dt0 = 0.0   # No vertical motion
dphi_dt0 = 0.8     # Initial orbital velocity

# Time parameters
t_span = 40.0
n_points = 1000
tau = np.linspace(0, t_span, n_points)

# Initial state
state0 = [r0, theta0, phi0, dr_dt0, dtheta_dt0, dphi_dt0]

# Integration with more reasonable tolerances
solution = odeint(
    geodesic_equation, 
    state0, 
    tau,
    rtol=1e-6,
    atol=1e-6,
    mxstep=5000
)

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

# Animation with 1.2 second repeat interval
ani = FuncAnimation(
    fig, 
    update, 
    frames=len(tau), 
    init_func=init, 
    blit=True, 
    interval=100/len(tau),  # Total time of 1.2 seconds divided by number of frames
    repeat=True              # Enable animation repeat
)

plt.legend()
plt.show()
