import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Higgs Field parameters
mu = 1.0
lmbda = 1.0

# Simulation parameters
num_particles = 50
field_strength = 5
timesteps = 100
min_velocity = 0.2  # Minimum allowed velocity
boost_interval = 1.2  # Time interval in seconds for fast rebounding
boost_duration = 0.4  # Duration of boost (seconds)
boost_factor = 2.2  # Factor by which light particles move faster during boost
decay_rate = 0.98  # Energy decay factor
revival_interval = 5.0  # Time interval for reappearance (seconds)
initial_boost_velocity = 4.0  # Initial velocity after reappearance
particle_visibility = np.ones(num_particles, dtype=bool)  # Visibility control

# Positions and velocities of the particles
positions = np.random.rand(num_particles, 3) * 10  # Particles in a 10x10x10 space
velocities = (np.random.rand(num_particles, 3) - 0.5) * 2  # Velocities

# Assign random masses to the particles
masses = np.random.rand(num_particles) * 2 + 0.5

# Speed control parameters
max_velocity = 8.0  # Increased from 5.0 to 8.0

def clip_velocity(velocity, max_speed=max_velocity):
    """Limits velocity magnitude while maintaining direction"""
    speed = np.linalg.norm(velocity)
    if speed > max_speed:
        return velocity * (max_speed / speed)
    return velocity

# Function to calculate the resistance in the field
def calculate_resistance(mass):
    phi = mass
    potential = -mu**2 * phi**2 + lmbda * phi**4
    resistance = np.clip(field_strength / (potential if potential != 0 else 1), 0.1, 100.0)
    return resistance

# Identify the lightest particles (top 25%)
light_particle_threshold = np.percentile(masses, 25)  # Mass threshold for "light" particles

# 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
scat = ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                  c=masses, cmap='viridis', s=50)

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_zlim(0, 10)
ax.set_title('Higgs Field Simulation')
cb = plt.colorbar(scat, ax=ax, pad=0.1, label='Mass (interaction with the field)')

# Set window position
plt.get_current_fig_manager().window.wm_geometry("+1000+100")  # Move window to position

# Initial view configuration
ax.view_init(elev=30, azim=30)  # Fixed view

# Time tracking for the simulation
time_counter = 0  # Keeps track of simulation time

# Function to update the animation
def update(frame):
    global positions, velocities, time_counter, particle_visibility

    time_counter += 0.05
    
    # Revisar si es momento de revivir las partículas
    if time_counter % revival_interval < 0.05:
        light_mask = masses < light_particle_threshold
        particle_visibility[light_mask] = True
        # Velocidades iniciales más altas pero controladas
        new_velocities = (np.random.rand(np.sum(light_mask), 3) - 0.5) * initial_boost_velocity
        # Aplicar límite a cada velocidad nueva
        for idx, vel in enumerate(new_velocities):
            new_velocities[idx] = clip_velocity(vel)
        velocities[light_mask] = new_velocities

    for i in range(num_particles):
        if not particle_visibility[i]:
            continue

        drag = calculate_resistance(masses[i])
        velocities[i] = velocities[i] * (1 - np.clip(drag * 0.1, 0, 1))
        
        # Partículas livianas con boost temporal
        if masses[i] < light_particle_threshold:
            velocities[i] *= decay_rate
            
            # Aplicar boost solo durante el intervalo específico
            time_since_revival = time_counter % revival_interval
            if time_since_revival < boost_duration:
                velocities[i] *= boost_factor
                # Limitar la velocidad después del boost
                velocities[i] = clip_velocity(velocities[i])
            
            # Hacer desaparecer si la velocidad es muy baja
            if np.linalg.norm(velocities[i]) < min_velocity:
                particle_visibility[i] = False

        # Limitar velocidad para todas las partículas
        velocities[i] = clip_velocity(velocities[i])

        # Handle bounces with damping
        for j in range(3):
            if positions[i, j] < 0:
                positions[i, j] = 0.1
                velocities[i, j] = abs(velocities[i, j]) * 0.9  # 10% energy loss on bounce
            elif positions[i, j] > 10:
                positions[i, j] = 9.9
                velocities[i, j] = -abs(velocities[i, j]) * 0.9  # 10% energy loss on bounce

        # Actualizar posiciones
        positions[i] += velocities[i] * 0.1

    # Actualizar el scatter plot solo con partículas visibles
    visible_positions = positions[particle_visibility]
    visible_masses = masses[particle_visibility]
    
    scat._offsets3d = (visible_positions[:, 0], 
                       visible_positions[:, 1], 
                       visible_positions[:, 2])
    scat.set_array(visible_masses)
    return scat,

# Animation
ani = FuncAnimation(fig, update, frames=timesteps, interval=50)

# Show the simulation
plt.show()
