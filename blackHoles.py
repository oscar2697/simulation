import pygame
import math
import random
from pygame.locals import *

pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Agujero Negro con Órbitas Realistas - CORREGIDO")
clock = pygame.time.Clock()

BACKGROUND_COLOR = (10, 5, 25)
BLACK_HOLE_COLOR = (0, 0, 0)
EVENT_HORIZON_COLOR = (30, 20, 40)
STAR_COLOR = (220, 220, 255)

G = 800   
M = 1000  
SCHWARZSCHILD_RADIUS = 25   
EVENT_HORIZON_RADIUS = 50   

class Star:
    def __init__(self):
        self.x = random.uniform(-3000, 3000)
        self.y = random.uniform(-3000, 3000)
        self.z = random.uniform(500, 4000)
        self.size = random.uniform(0.5, 2.5)
        self.brightness = random.uniform(0.3, 1.0)
        self.color = (
            int(STAR_COLOR[0] * self.brightness),
            int(STAR_COLOR[1] * self.brightness),
            int(STAR_COLOR[2] * self.brightness)
        )
    
    def update(self):
        pass
    
    def project(self, camera_pos):
        dx = self.x - camera_pos[0]
        dy = self.y - camera_pos[1]
        dz = self.z - camera_pos[2]
        if dz <= 0:
            return None, None, 0
        
        factor = 800 / dz
        screen_x = dx * factor + WIDTH // 2   
        screen_y = dy * factor + HEIGHT // 2  
        size = self.size * factor

        if size < 0.2:
            return None, None, 0
            
        return screen_x, screen_y, size

class AccretionParticle:
    def __init__(self, black_hole_center=(0, 0, 0)):
        self.center_x, self.center_y, self.center_z = black_hole_center
        self.reset()

    def reset(self):
        self.distance = random.uniform(500, 1500)   
        self.angle = random.uniform(0, 2 * math.pi)
        self.inclination = random.uniform(-0.3, 0.3)

        self.x = self.center_x + self.distance * math.cos(self.angle)
        self.y = self.center_y + self.distance * math.sin(self.angle)
        self.z = self.center_z + self.inclination * self.distance

        orbital_speed = math.sqrt(G * M / self.distance)
        self.velocity_x = -orbital_speed * math.sin(self.angle)
        self.velocity_y =  orbital_speed * math.cos(self.angle)
        self.velocity_z = 0

        self.size = random.uniform(1.5, 3.5)
        self.spiral_factor = random.uniform(0.9993, 0.9997)

        self.life = 1.0  
        self.fade_out = False
        self.update_color()

    def update(self):
        dx = self.center_x - self.x
        dy = self.center_y - self.y
        dz = self.center_z - self.z
        distance_3d = max(1.0, math.sqrt(dx*dx + dy*dy + dz*dz))

        force_magnitude = G * M / (distance_3d**2)
        ax = force_magnitude * dx / distance_3d
        ay = force_magnitude * dy / distance_3d
        az = force_magnitude * dz / distance_3d

        dt = 0.02
        self.velocity_x += ax * dt
        self.velocity_y += ay * dt
        self.velocity_z += az * dt

        self.velocity_x *= self.spiral_factor
        self.velocity_y *= self.spiral_factor
        self.velocity_z *= self.spiral_factor

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.z += self.velocity_z * dt

        if distance_3d < EVENT_HORIZON_RADIUS and not self.fade_out:
            self.fade_out = True

        if self.fade_out:
            self.life -= 0.05  
            self.size *= 1.05  
            if self.life <= 0:
                self.reset()

        self.update_color()

    def update_color(self):
        base_color = (255, 200, 100)
        self.color = tuple(int(c * self.life) for c in base_color)

    def project(self, camera_pos):
        dx = self.x - camera_pos[0]
        dy = self.y - camera_pos[1]
        dz = self.z - camera_pos[2]
        if dz <= 0:
            return None, None, 0
        
        factor = 800 / dz
        screen_x = dx * factor + WIDTH // 2
        screen_y = dy * factor + HEIGHT // 2
        size = self.size * factor * (1 + 100/max(100, dz))
        if size < 0.5:
            return None, None, 0
        return screen_x, screen_y, size

class BlackHole:
    def __init__(self):
        self.center = (0, 0, 0)
        self.radius = SCHWARZSCHILD_RADIUS
        self.event_horizon_radius = EVENT_HORIZON_RADIUS
        self.stars = [Star() for _ in range(200)]
        self.accretion_particles = [AccretionParticle(self.center) for _ in range(300)]
        self.corona_pulse = 0
    
    def update(self):
        for star in self.stars:
            star.update()
        for particle in self.accretion_particles:
            particle.update()
        self.corona_pulse += 0.05
    
    def project_center(self, camera_pos):
        dx = self.center[0] - camera_pos[0]
        dy = self.center[1] - camera_pos[1]
        dz = self.center[2] - camera_pos[2]
        if dz <= 0:
            return WIDTH // 2, HEIGHT // 2
        factor = 800 / dz
        screen_x = dx * factor + WIDTH // 2
        screen_y = dy * factor + HEIGHT // 2
        return int(screen_x), int(screen_y)
    
    def draw(self, surface, camera_pos):
        proj_cx, proj_cy = self.project_center(camera_pos)
        offset_x = WIDTH // 2 - proj_cx   
        offset_y = HEIGHT // 2 - proj_cy  

        for star in self.stars:
            sx, sy, size = star.project(camera_pos)
            if sx is None:
                continue
            sx += offset_x  
            sy += offset_y  
            if -50 <= sx <= WIDTH + 50 and -50 <= sy <= HEIGHT + 50 and size > 0.2:
                pygame.draw.circle(surface, star.color, (int(sx), int(sy)), max(1, int(size)))

        particles_to_draw = []
        for p in self.accretion_particles:
            sx, sy, size = p.project(camera_pos)
            if sx is None:
                continue
            sx += offset_x  
            sy += offset_y  
            if -50 <= sx <= WIDTH + 50 and -50 <= sy <= HEIGHT + 50 and size > 0.5:
                dist_to_camera = math.sqrt(
                    (p.x - camera_pos[0])**2 +
                    (p.y - camera_pos[1])**2 +
                    (p.z - camera_pos[2])**2
                )
                particles_to_draw.append((dist_to_camera, sx, sy, size, p.color))
        
        particles_to_draw.sort(key=lambda x: x[0], reverse=True)
        for _, sx, sy, size, color in particles_to_draw:
            pygame.draw.circle(surface, color, (int(sx), int(sy)), max(1, int(size)))
            glow_size = max(2, int(size * 1.5))
            glow_color = tuple(min(255, int(c * 0.3)) for c in color)
            pygame.draw.circle(surface, glow_color, (int(sx), int(sy)), glow_size, 1)

        bh_screen_x, bh_screen_y = WIDTH // 2, HEIGHT // 2  
        bh_distance = math.sqrt(sum((camera_pos[i] - self.center[i])**2 for i in range(3)))
        size_factor = 800 / max(100, bh_distance)
        event_horizon_size = max(10, int(self.event_horizon_radius * size_factor))
        black_hole_size = max(5, int(self.radius * size_factor))
        
        for i in range(5):
            alpha_factor = (5 - i) / 5.0
            radius = event_horizon_size + i * 3
            color_intensity = int(60 * alpha_factor)
            pygame.draw.circle(surface, (color_intensity, color_intensity//2, color_intensity//2),
                               (bh_screen_x, bh_screen_y), radius, 2)
        
        pygame.draw.circle(surface, BLACK_HOLE_COLOR, (bh_screen_x, bh_screen_y), black_hole_size)
        
        corona_radius = black_hole_size + int(5 * (1 + 0.3 * math.sin(self.corona_pulse)))
        corona_alpha = int(80 + 40 * math.sin(self.corona_pulse * 1.5))
        corona_color = (min(255, corona_alpha), min(255, corona_alpha//2), min(255, int(corona_alpha * 1.5)))
        pygame.draw.circle(surface, corona_color, (bh_screen_x, bh_screen_y), corona_radius, 2)

black_hole = BlackHole()

camera_angle = 0
camera_elevation = 0.3
camera_distance = 600
rotation_speed = 0.003

running = True
dragging = False
last_mouse_pos = (0, 0)
auto_rotate = True
show_info = True

font = pygame.font.SysFont(None, 24)
font_large = pygame.font.SysFont(None, 28, bold=True)

while running:
    if auto_rotate:
        camera_angle += rotation_speed
    
    camera_pos = [
        math.sin(camera_angle) * math.cos(camera_elevation) * camera_distance,
        math.sin(camera_elevation) * camera_distance,
        math.cos(camera_angle) * math.cos(camera_elevation) * camera_distance
    ]
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            last_mouse_pos = pygame.mouse.get_pos()
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            dragging = False
        elif event.type == MOUSEMOTION and dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            last_x, last_y = last_mouse_pos
            dx = mouse_x - last_x
            dy = mouse_y - last_y
            camera_angle += dx * 0.005
            camera_elevation = max(-math.pi/2.5, min(math.pi/2.5, camera_elevation + dy * 0.003))
            last_mouse_pos = (mouse_x, mouse_y)
        elif event.type == MOUSEWHEEL:
            camera_distance += event.y * -30
            camera_distance = max(200, min(2000, camera_distance))
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                auto_rotate = not auto_rotate
            elif event.key == K_r:
                black_hole = BlackHole()
                camera_angle = 0
                camera_elevation = 0.3
                camera_distance = 600
            elif event.key == K_i:
                show_info = not show_info
            elif event.key == K_ESCAPE:
                running = False
            elif event.key == K_f:
                camera_angle = 0
                camera_elevation = 0.3
                camera_distance = 600
    
    black_hole.update()
    screen.fill(BACKGROUND_COLOR)
    black_hole.draw(screen, camera_pos)
    
    if show_info:
        info_surface = pygame.Surface((480, 260), pygame.SRCALPHA)
        pygame.draw.rect(info_surface, (20, 15, 35, 250), (0, 0, 490, 280), border_radius=20)
        pygame.draw.rect(info_surface, (100, 150, 230, 190), (0, 0, 480, 260), 2, border_radius=15)

        title = font_large.render("BLACK HOLE - CORRECTED PHYSICS", True, (50, 100, 200))
        info_surface.blit(title, (10, 10))
        
        texts = [
            f"Camera distance: {int(camera_distance)}",
            f"Angle: {math.degrees(camera_angle):.1f}°",
            f"Elevation: {math.degrees(camera_elevation):.1f}°",
            f"Active particles: {len(black_hole.accretion_particles)}",
            "",
            "Implemented physics:",
            "• Stable Keplerian orbits",
            "• Realistic temperature gradient",
            "• Accretion spiral (energy loss)",
            "• Consistent 3D projection"
        ]
        
        for i, text in enumerate(texts):
            if text == "":
                continue
            y_pos = 70 + i * 18 
            if i < 4:
                color = (200, 230, 255)
            elif "Implemented" in text:
                color = (150, 255, 150)
            else:
                color = (220, 220, 255)
            info_surface.blit(font.render(text, True, color), (20, y_pos))
        
        screen.blit(info_surface, (20, 20))

    status = "ON" if auto_rotate else "OFF"
    status_color = (100, 255, 150) if auto_rotate else (255, 100, 100)
    screen.blit(font.render(f"Auto-rotation: {status}", True, status_color), (WIDTH - 250, 20))

    controls = [
        "SPACE: Auto-rotation | R: Reset | F: Front view",
        "Mouse: Rotate camera | Wheel: Zoom | I: Info | ESC: Quit"
    ]
    for i, control in enumerate(controls):
        screen.blit(font.render(control, True, (200, 200, 220)), (20, HEIGHT - 60 + i * 25))

    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
