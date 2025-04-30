from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import sys

# Game variables
BATTLEFIELD_SIZE = 1000  # Size of the battlefield
player_pos = [0, 0, 50]  # Player position (x, y, z)
player_rotation = 90  # Player rotation in degrees (start at 90 degrees)
player_speed = 10  # Player movement speed - increased from 5 to 10
player_boost_speed = 15  # Faster speed for quick maneuvers
player_health = 1000  # Player health (new)
max_player_health = 1000  # Maximum player health (new)
damage_cooldown = 0  # Cooldown timer after taking damage (new)
current_level = 1  # Current game level (new)
enemies = []  # List to store enemy positions
bullets = []  # List to store laser beam positions
enemy_bullets = []  # List to store enemy laser beams (new)
score = 0  # Player score
game_over = False  # Game over flag
HUD_color = (0, 1, 1)  # Cyan color for HUD elements
health_bar_color = (0, 1, 0)  # Green color for health bar (new)

# Movement effect variables
moving_forward = False  # Flag for forward movement
moving_backward = False  # Flag for backward movement
thruster_glow_intensity = 0.0  # Base thruster glow intensity
thruster_particles = []  # List to store thruster particle effects

# Camera-related variables
camera_mode = 0  # 0 = third-person, 1 = cockpit
camera_pos = (0, -200, 200)  # Behind and above player
camera_distance = 250  # Distance from player in third-person view
fovY = 60  # Field of view

# Grid animation variables
grid_offset_x = 0  # X-offset for grid animation
grid_offset_y = 0  # Y-offset for grid animation
grid_line_spacing = 100  # Spacing between grid lines
grid_animation_speed = 5  # Speed of grid animation

# Enemy type definitions
ENEMY_TYPES = {
    # Level 1: Basic fighters (red)
    1: {
        "hull_color": (0.4, 0.1, 0.1),      # Dark red
        "accent_color": (1.0, 0.2, 0.0),    # Bright red
        "health": 100,                       # Base health
        "speed": 1.5,                        # Movement speed (reduced from 3)
        "damage": 100,                       # Damage per hit
        "firing_rate": 120,                  # Frames between shots (higher = slower)
        "follow_distance": 400,              # Distance to start following player
        "firing_distance": 350,              # Distance to start firing
        "bullet_speed": 12,                  # Bullet speed (reduced from 15)
        "bullet_color": (1.0, 0.2, 0.0),    # Bullet color (red)
        "bullet_lifetime": 100,              # Bullet lifetime
        "score_value": 100                   # Score awarded for destroying
    },
    
    # Level 2: Advanced fighters (orange)
    2: {
        "hull_color": (0.4, 0.2, 0.0),      # Dark orange
        "accent_color": (1.0, 0.5, 0.0),    # Bright orange
        "health": 150,                       # More health
        "speed": 2,                          # Faster (reduced from 4)
        "damage": 120,                       # More damage
        "firing_rate": 100,                  # Faster firing rate
        "follow_distance": 450,              # Longer detection range
        "firing_distance": 400,              # Longer firing range
        "bullet_speed": 14,                  # Faster bullets (reduced from 17)
        "bullet_color": (1.0, 0.5, 0.0),    # Bullet color (orange)
        "bullet_lifetime": 120,              # Longer bullet lifetime
        "score_value": 150                   # Higher score value
    },
    
    # Level 3: Elite fighters (purple)
    3: {
        "hull_color": (0.3, 0.0, 0.3),      # Dark purple
        "accent_color": (0.7, 0.0, 1.0),    # Bright purple
        "health": 200,                       # Even more health
        "speed": 2.5,                        # Even faster (reduced from 5)
        "damage": 150,                       # More damage
        "firing_rate": 80,                   # Even faster firing rate
        "follow_distance": 500,              # Longer detection range
        "firing_distance": 450,              # Longer firing range
        "bullet_speed": 16,                  # Faster bullets (reduced from 20)
        "bullet_color": (0.7, 0.0, 1.0),    # Bullet color (purple)
        "bullet_lifetime": 150,              # Longer bullet lifetime
        "score_value": 200                   # Higher score value
    },
    
    # Level 4: Boss ships (green/toxic)
    4: {
        "hull_color": (0.1, 0.3, 0.1),      # Dark green
        "accent_color": (0.0, 1.0, 0.2),    # Bright toxic green
        "health": 350,                       # Very high health
        "speed": 1.8,                        # Balanced speed (reduced from 3.5)
        "damage": 200,                       # High damage
        "firing_rate": 60,                   # Rapid firing rate
        "follow_distance": 550,              # Long detection range
        "firing_distance": 500,              # Long firing range
        "bullet_speed": 15,                  # Fast bullets (reduced from 18)
        "bullet_color": (0.0, 1.0, 0.2),    # Bullet color (green)
        "bullet_lifetime": 180,              # Very long bullet lifetime
        "score_value": 300                   # High score value
    }
}

# Level configurations
LEVEL_CONFIG = {
    1: {
        "enemy_count": 10,                    # Number of enemies
        "enemy_types": [1],                   # Types of enemies to spawn (from ENEMY_TYPES)
        "next_level_score": 1000,             # Score needed to advance
        "battlefield_color": (0.2, 0.4, 0.8)  # Grid color
    },
    2: {
        "enemy_count": 12,
        "enemy_types": [1, 2],                # Mix of level 1 and 2 enemies
        "next_level_score": 2500,
        "battlefield_color": (0.3, 0.4, 0.7)
    },
    3: {
        "enemy_count": 15,
        "enemy_types": [2, 3],                # Mix of level 2 and 3 enemies
        "next_level_score": 4500,
        "battlefield_color": (0.4, 0.3, 0.6)
    },
    4: {
        "enemy_count": 10,
        "enemy_types": [3, 4],                # Mix of level 3 and boss enemies
        "next_level_score": 99999,            # Very high - effectively the final level
        "battlefield_color": (0.2, 0.5, 0.5)
    }
}


# Initialize some enemies
def initialize_enemies():
    global enemies, current_level
    
    enemies = []  # Clear existing enemies
    
    level_data = LEVEL_CONFIG.get(current_level, LEVEL_CONFIG[1])  # Default to level 1 if invalid
    enemy_count = level_data["enemy_count"]
    enemy_types = level_data["enemy_types"]
    
    for i in range(enemy_count):
        # Select a random enemy type from the available types for this level
        enemy_type = random.choice(enemy_types)
        
        # Get enemy type data
        type_data = ENEMY_TYPES[enemy_type]
        
        enemies.append([
            random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),  # x
            random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),  # y
            random.uniform(100, 500),                                 # z (height)
            random.uniform(0, 360),                                   # rotation
            enemy_type,                                               # enemy type (new)
            type_data["health"],                                      # health (new)
            0,                                                        # firing cooldown (new)
            0                                                         # behavior state (new)
        ])

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(*HUD_color)  # Use HUD color
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_spaceship(is_player=True):
    """Draw a spaceship (player battleship or enemy)"""
    if is_player:
        # Battleship style for player
        draw_battleship()
    else:
        # Simpler design for enemies
        draw_enemy_ship()

def draw_battleship():
    """Draw a sci-fi battleship-style spaceship for the player"""
    # Colors for sci-fi effect
    hull_color = (0.2, 0.25, 0.35)         # Dark blue-gray
    accent_color = (0.0, 0.8, 1.0)         # Neon blue
    deck_color = (0.3, 0.35, 0.45)         # Slightly lighter
    turret_color = (0.15, 0.18, 0.22)      # Darker for turrets
    energy_core_color = (0.0, 1.0, 0.7)    # Glowing teal
    engine_glow_color = (1.0, 0.5, 0.1)    # Orange
    highlight_color = (0.7, 0.9, 1.0)      # Light blue highlight

    # Main hull - angular, layered
    glPushMatrix()
    glColor3f(*hull_color)
    glScalef(3.2, 1.1, 0.5)
    glutSolidCube(30)
    glPopMatrix()

    # Lower hull accent (angular)
    glPushMatrix()
    glColor3f(*accent_color)
    glTranslatef(0, 0, -7)
    glScalef(2.8, 0.7, 0.15)
    glutSolidCube(30)
    glPopMatrix()

    # Upper deck (layered)
    glPushMatrix()
    glColor3f(*deck_color)
    glTranslatef(0, 0, 10)
    glScalef(2.5, 0.8, 0.18)
    glutSolidCube(30)
    glPopMatrix()

    # Command tower (superstructure)
    glPushMatrix()
    glColor3f(*highlight_color)
    glTranslatef(-13, 0, 18)
    glScalef(0.7, 0.5, 0.7)
    glutSolidCube(20)
    # Energy core on top
    glColor3f(*energy_core_color)
    glTranslatef(0, 0, 15)
    glutSolidSphere(4, 12, 12)
    glPopMatrix()

    # Front bow - sharp, sci-fi cone
    glPushMatrix()
    glColor3f(*accent_color)
    glTranslatef(55, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCone(15, 40, 16, 16)
    glPopMatrix()

    # Rear section - layered cones
    glPushMatrix()
    glColor3f(*hull_color)
    glTranslatef(-55, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glutSolidCone(15, 25, 12, 12)
    glColor3f(*engine_glow_color)
    glTranslatef(0, 0, -10)
    glutSolidCone(10, 15, 10, 10)
    glPopMatrix()

    # Main gun turrets - angular, sci-fi
    draw_turret(35, 0, 13, turret_color, accent_color)
    draw_turret(10, 0, 13, turret_color, accent_color)
    draw_turret(-20, 0, 13, turret_color, accent_color)

    # Secondary gun turrets (smaller, more)
    draw_secondary_turret(40, 12, 11, accent_color)
    draw_secondary_turret(40, -12, 11, accent_color)
    draw_secondary_turret(20, 15, 11, accent_color)
    draw_secondary_turret(20, -15, 11, accent_color)
    draw_secondary_turret(-35, 12, 11, accent_color)
    draw_secondary_turret(-35, -12, 11, accent_color)

    # Winglets - sci-fi fins
    for angle, y_offset in [(-30, 25), (30, -25)]:
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(10, y_offset, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(1.2, 0.2, 0.05)
        glutSolidCube(60)
        glPopMatrix()

    # Lower fins
    for y_offset in [-18, 18]:
        glPushMatrix()
        glColor3f(*highlight_color)
        glTranslatef(-10, y_offset, -10)
        glScalef(0.5, 0.1, 0.02)
        glutSolidCube(60)
        glPopMatrix()

    # Engines (thrusters)
    draw_engines(engine_glow_color, accent_color)

def draw_turret(x, y, z, color, accent_color):
    """Draw a main gun turret at position x,y,z with sci-fi accent"""
    glPushMatrix()
    glTranslatef(x, y, z)
    # Turret base
    glColor3f(*color)
    glutSolidSphere(7, 12, 12)
    # Accent ring
    glColor3f(*accent_color)
    glScalef(1.2, 1.2, 0.4)
    glutSolidSphere(6, 12, 12)
    # Main guns (triple barrels)
    glColor3f(0.2, 0.8, 1.0)
    for offset in [-2, 0, 2]:
        glPushMatrix()
        glTranslatef(8, offset, 2)
        glRotatef(90, 0, 1, 0)
        glutSolidCone(2, 18, 8, 1)
        glPopMatrix()
    glPopMatrix()

def draw_secondary_turret(x, y, z, accent_color):
    """Draw a smaller secondary turret with accent"""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*accent_color)
    glutSolidSphere(4, 8, 8)
    # Single gun
    glColor3f(0.2, 0.8, 1.0)
    glPushMatrix()
    glTranslatef(5, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCone(1, 12, 8, 1)
    glPopMatrix()
    glPopMatrix()

def draw_engines(engine_glow_color, accent_color):
    """Draw the battleship engines with sci-fi glow and accents"""
    global thruster_glow_intensity, moving_forward, moving_backward
    
    # Set base thruster color based on movement state
    if moving_forward:
        # Cyan color when moving forward (pressing W)
        base_glow = [0.0, 0.8, 1.0]
    else:
        # Default orange color when not moving forward or moving backward
        base_glow = [1.0, 0.5, 0.1]
    
    # Enhance glow based on movement intensity
    enhanced_glow = [
        min(1.0, base_glow[0] + thruster_glow_intensity * 0.2),
        min(1.0, base_glow[1] + thruster_glow_intensity * 0.2),
        min(1.0, base_glow[2] + thruster_glow_intensity * 0.2)
    ]
    
    # Size multiplier based on thruster intensity - bigger when moving
    size_mult = 1.0 + thruster_glow_intensity * 0.8
    
    # Draw large central thruster housing
    glPushMatrix()
    glTranslatef(-55, 0, 0)
    glColor3f(*accent_color)
    # Slightly smaller scale for the main thruster
    glScalef(0.4, 0.5, 0.5)
    glutSolidCube(40)
    glPopMatrix()
    
    # Draw large central thruster glow
    glPushMatrix()
    glTranslatef(-65, 0, 0)
    
    # Engine glow - changes color and size with movement
    glColor3f(*enhanced_glow)
    # Reduced size but still larger than original
    glutSolidSphere(10 * size_mult, 16, 16)
    
    # Add additional glow effect when moving
    if thruster_glow_intensity > 0.2:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Outer glow
        if moving_forward:
            outer_glow = [0.2, 0.8, 1.0, 0.7 * thruster_glow_intensity]  # Cyan outer glow
        else:
            outer_glow = [1.0, 0.6, 0.1, 0.7 * thruster_glow_intensity]  # Orange outer glow
            
        glColor4f(*outer_glow)
        glutSolidSphere(14 * size_mult, 16, 16)
        
        # Thruster trail (large cone)
        glPushMatrix()
        glTranslatef(-15, 0, 0)
        glRotatef(-90, 0, 1, 0)
        
        # Cone color based on movement
        if moving_forward:
            cone_glow = [0.0, 0.7, 1.0, 0.6 * thruster_glow_intensity]  # Cyan flame
            inner_cone = [0.3, 0.8, 1.0, 0.8 * thruster_glow_intensity]  # Brighter cyan inner
        else:
            cone_glow = [1.0, 0.5, 0.0, 0.6 * thruster_glow_intensity]  # Orange flame
            inner_cone = [1.0, 0.7, 0.2, 0.8 * thruster_glow_intensity]  # Yellow-orange inner
            
        glColor4f(*cone_glow)
        glutSolidCone(12 * size_mult, 35 * size_mult, 16, 8)
        
        # Inner cone (brighter)
        glColor4f(*inner_cone)
        glutSolidCone(8 * size_mult, 25 * size_mult, 12, 8)
        
        glDisable(GL_BLEND)
        glPopMatrix()
    
    glPopMatrix()
    
    # Additional small thrusters on the sides (for maneuvering)
    for y_offset in [-18, 18]:
        glPushMatrix()
        glTranslatef(-50, y_offset, 0)
        glColor3f(*accent_color)
        glScalef(0.2, 0.2, 0.2)
        glutSolidCube(20)
        
        # Small side thruster glow - same color as main thruster
        glColor3f(*enhanced_glow)
        glTranslatef(-5, 0, 0)
        glutSolidSphere(4 * size_mult, 8, 8)
        glPopMatrix()
    
    # Extra glowing energy core at the rear
    glPushMatrix()
    # Energy core changes color with movement
    if moving_forward:
        glColor3f(0.0, 0.8, 1.0)  # Cyan for forward
    else:
        glColor3f(1.0, 0.6, 0.2)  # Orange for idle/backward
    
    glTranslatef(-60, 0, 12)  # Positioned above the main thruster
    glutSolidSphere(6 + thruster_glow_intensity * 2, 12, 12)  # Adjusted energy core size
    glPopMatrix()
    
    # Add energy conduits connecting to the main thruster
    glPushMatrix()
    # Conduit color matches thruster state
    if moving_forward:
        glColor3f(0.0, 0.8, 1.0)  # Cyan for forward
    else:
        glColor3f(1.0, 0.6, 0.2)  # Orange for idle/backward
    
    # Horizontal conduit
    glTranslatef(-58, 0, 6)
    glScalef(0.1, 0.1, 0.6)
    glutSolidCube(30)
    glPopMatrix()
    
    # Draw thruster particles when moving forward (but not when moving backward)
    if thruster_glow_intensity > 0 and not moving_backward:
        draw_thruster_particles()

def draw_thruster_particles():
    """Draw particle effects for thrusters"""
    global thruster_particles, moving_forward, moving_backward
    
    # Only draw particles if there are any and thruster effect is active
    if not thruster_particles or thruster_glow_intensity <= 0:
        return
        
    glPushMatrix()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glDepthMask(GL_FALSE)
    
    # Draw each particle
    glPointSize(4)  # Larger particles
    glBegin(GL_POINTS)
    
    for particle in thruster_particles:
        # Fade out based on lifetime
        alpha = particle[3] / 40.0  # Lifetime based alpha
        
        if moving_forward:
            # Cyan particles when moving forward
            glColor4f(0.0, 0.8 * alpha, 1.0, alpha)  # Cyan to blue
        else:
            # Orange particles when idle
            glColor4f(1.0, 0.5 * alpha, 0.0, alpha)  # Orange to darker orange
        
        glVertex3f(particle[0], particle[1], particle[2])
    glEnd()
    
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_enemy_ship(enemy_type=1):
    """Draw enemy spaceship based on enemy type"""
    # Get colors for this enemy type
    type_data = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES[1])  # Default to type 1 if invalid
    hull_color = type_data["hull_color"]
    accent_color = type_data["accent_color"]
    energy_core_color = accent_color  # Use accent color for energy core
    engine_glow_color = (1.0, 0.5, 0.0)  # Orange engine glow for all types
    
    # Size multiplier based on enemy type (bosses are bigger)
    size_mult = 1.0
    if enemy_type == 4:  # Boss type
        size_mult = 1.5
    
    # Main hull - angular design that varies by type
    glPushMatrix()
    glColor3f(*hull_color)
    
    if enemy_type <= 2:  # Type 1-2: Flat, sleek design
        glScalef(2.5 * size_mult, 0.9 * size_mult, 0.4 * size_mult)
        glutSolidCube(25)
    elif enemy_type == 3:  # Type 3: More angular, aggressive design
        glScalef(2.2 * size_mult, 1.1 * size_mult, 0.5 * size_mult)
        glutSolidCube(25)
    else:  # Type 4 (Boss): Bulkier design
        glScalef(2.0 * size_mult, 1.3 * size_mult, 0.7 * size_mult)
        glutSolidCube(30)
    glPopMatrix()
    
    # Upper section
    glPushMatrix()
    glColor3f(*accent_color)
    glTranslatef(0, 0, 8 * size_mult)
    
    if enemy_type <= 2:  # Type 1-2: Flat top
        glScalef(2.0 * size_mult, 0.7 * size_mult, 0.15 * size_mult)
        glutSolidCube(25)
    elif enemy_type == 3:  # Type 3: More pronounced top
        glScalef(1.8 * size_mult, 0.8 * size_mult, 0.2 * size_mult)
        glutSolidCube(25)
    else:  # Type 4 (Boss): Elevated command deck
        glScalef(1.6 * size_mult, 1.0 * size_mult, 0.25 * size_mult)
        glutSolidCube(30)
    glPopMatrix()
    
    # Front section - varies by type
    glPushMatrix()
    glColor3f(*hull_color)
    
    if enemy_type == 1:  # Type 1: Triangular nose
        glTranslatef(25 * size_mult, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidCone(10 * size_mult, 25 * size_mult, 12, 12)
    elif enemy_type == 2:  # Type 2: More angular nose
        glTranslatef(30 * size_mult, 0, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidCone(12 * size_mult, 30 * size_mult, 8, 8)
    elif enemy_type == 3:  # Type 3: Sharper, more alien nose
        glTranslatef(28 * size_mult, 0, 0)
        glRotatef(90, 0, 1, 0)
        glScalef(1.0, 1.4, 1.0)  # Flattened vertically
        glutSolidCone(10 * size_mult, 35 * size_mult, 8, 8)
    else:  # Type 4 (Boss): Double-pronged front
        # First prong
        glTranslatef(30 * size_mult, 10 * size_mult, 0)
        glRotatef(90, 0, 1, 0)
        glutSolidCone(8 * size_mult, 40 * size_mult, 8, 8)
        # Second prong
        glTranslatef(0, -20 * size_mult, 0)
        glutSolidCone(8 * size_mult, 40 * size_mult, 8, 8)
    glPopMatrix()
    
    # Side wings/fins - shape varies by type
    y_offsets = [(20, 20), (-20, -20)]  # Default wing positions and angles
    if enemy_type == 3:
        y_offsets = [(25, 25), (-25, -25)]  # Type 3: Wider wings
    elif enemy_type == 4:
        y_offsets = [(30, 30), (-30, -30), (15, 15), (-15, -15)]  # Type 4: Four wings
    
    for y_offset, angle in y_offsets:
        glPushMatrix()
        glColor3f(*accent_color)
        glTranslatef(0, y_offset * size_mult, 0)
        glRotatef(angle, 0, 0, 1)
        
        if enemy_type <= 2:  # Type 1-2: Standard wings
            glScalef(1.0 * size_mult, 0.15 * size_mult, 0.1 * size_mult)
            glutSolidCube(50)
        elif enemy_type == 3:  # Type 3: More angular wings
            glScalef(1.2 * size_mult, 0.12 * size_mult, 0.1 * size_mult)
            glutSolidCube(55)
        else:  # Type 4 (Boss): Shorter, thicker wings
            glScalef(0.8 * size_mult, 0.2 * size_mult, 0.12 * size_mult)
            glutSolidCube(60)
        glPopMatrix()
    
    # Weapons - number and position varies by type
    weapon_positions = [(-15, 0), (0, 0), (15, 0)]  # Default (type 1)
    
    if enemy_type == 2:
        weapon_positions = [(-20, 0), (-5, 0), (10, 0), (25, 0)]  # Type 2: More weapons
    elif enemy_type == 3:
        weapon_positions = [(-20, 0), (0, 0), (20, 0), (-10, 10), (10, -10)]  # Type 3: More spread
    elif enemy_type == 4:
        weapon_positions = [(-25, 0), (-15, 0), (-5, 0), (5, 0), (15, 0), (25, 0), 
                            (-20, 15), (0, 15), (20, 15), (-20, -15), (0, -15), (20, -15)]  # Type 4: Many weapons
    
    for x_offset, y_offset in weapon_positions:
        glPushMatrix()
        glTranslatef(x_offset * size_mult, y_offset * size_mult, 10 * size_mult)
        # Weapon base
        glColor3f(*hull_color)
        glutSolidSphere(3 * size_mult, 8, 8)
        # Weapon barrel
        glColor3f(*accent_color)
        glRotatef(-90, 1, 0, 0)
        glutSolidCylinder(1.5 * size_mult, 8 * size_mult, 8, 1)
        glPopMatrix()
    
    # Rear section with thruster
    glPushMatrix()
    glTranslatef(-40 * size_mult, 0, 0)
    
    # Thruster housing
    glColor3f(*hull_color)
    glScalef(0.3 * size_mult, 0.4 * size_mult, 0.4 * size_mult)
    glutSolidCube(35)
    glPopMatrix()
    
    # Engine glow
    glPushMatrix()
    glTranslatef(-46 * size_mult, 0, 0)
    glColor3f(*engine_glow_color)
    glutSolidSphere(6 * size_mult, 12, 12)
    glPopMatrix()
    
    # Side thrusters
    for y_offset in [-15, 15]:
        glPushMatrix()
        glTranslatef(-35 * size_mult, y_offset * size_mult, 0)
        # Thruster housing
        glColor3f(*hull_color)
        glScalef(0.2 * size_mult, 0.2 * size_mult, 0.2 * size_mult)
        glutSolidCube(20)
        # Thruster glow
        glTranslatef(-15, 0, 0)
        glColor3f(*engine_glow_color)
        glutSolidSphere(3 * size_mult, 8, 8)
        glPopMatrix()
    
    # Energy core on top (glowing) - larger and more complex for higher types
    glPushMatrix()
    glColor3f(*energy_core_color)
    
    if enemy_type <= 2:  # Type 1-2: Simple sphere
        glTranslatef(-25 * size_mult, 0, 12 * size_mult)
        glutSolidSphere(4 * size_mult, 10, 10)
    elif enemy_type == 3:  # Type 3: Pulsing sphere with ring
        glTranslatef(-25 * size_mult, 0, 15 * size_mult)
        glutSolidSphere(5 * size_mult, 12, 12)
        glColor3f(*hull_color)
        glRotatef(90, 1, 0, 0)
        glutSolidTorus(1 * size_mult, 7 * size_mult, 8, 16)
    else:  # Type 4 (Boss): Complex energy core
        glTranslatef(-25 * size_mult, 0, 18 * size_mult)
        glutSolidSphere(7 * size_mult, 16, 16)
        glColor3f(*hull_color)
        glRotatef(90, 1, 0, 0)
        glutSolidTorus(1.5 * size_mult, 9 * size_mult, 12, 24)
    glPopMatrix()
    
    # Thruster flame effects (always on for enemies)
    glPushMatrix()
    glTranslatef(-55 * size_mult, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 0.5, 0.0, 0.7)  # Orange flame
    glutSolidCone(5 * size_mult, 15 * size_mult, 8, 2)
    glColor4f(1.0, 0.7, 0.0, 0.5)  # Yellow-orange inner flame
    glutSolidCone(3 * size_mult, 10 * size_mult, 8, 2)
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_enemy_bullet(bullet_color):
    """Draw a laser beam from an enemy ship"""
    # Get the bullet color from the parameters
    glColor3f(*bullet_color)
    
    # Draw a long, thin beam using a scaled cube
    glPushMatrix()
    glScalef(20, 0.7, 0.7)  # Enemy bullets are slightly thicker but shorter
    glutSolidCube(5)
    glPopMatrix()
    
    # Add a glow effect
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glColor4f(bullet_color[0], bullet_color[1], bullet_color[2], 0.5)
    glPushMatrix()
    glScalef(22, 1.2, 1.2)  # Slightly larger for glow effect
    glutSolidCube(5)
    glPopMatrix()
    glDisable(GL_BLEND)

def draw_enemy_bullets():
    """Draw all enemy laser beams"""
    for bullet in enemy_bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glRotatef(bullet[3], 0, 0, 1)  # Rotate to match firing direction
        
        # Get enemy type and bullet color
        enemy_type = bullet[6]  # Store enemy type in bullet data
        bullet_color = ENEMY_TYPES[enemy_type]["bullet_color"]
        
        draw_enemy_bullet(bullet_color)
        glPopMatrix()

def draw_laser_beam():
    """Draw a laser beam"""
    glColor3f(1, 0, 0)  # Bright red for laser
    
    # Draw a long, thin beam using a scaled cube
    glPushMatrix()
    glScalef(30, 0.5, 0.5)  # Long in the x direction, thin in y and z
    glutSolidCube(5)
    glPopMatrix()

def draw_explosion(size):
    """Draw an explosion"""
    glColor3f(1, 0.5, 0)  # Orange
    glutSolidSphere(size, 10, 10)
    
    glPushMatrix()
    glColor3f(1, 0, 0)  # Red
    glutSolidSphere(size * 0.7, 8, 8)
    glPopMatrix()

def draw_radar():
    """Draw a radar in the corner of the screen"""
    glPushMatrix()
    
    # Set up orthographic projection for 2D overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Draw radar circle outline (no background fill)
    glColor3f(0, 0.7, 0.7)  # Cyan outline
    glBegin(GL_LINE_LOOP)
    for i in range(361):
        angle = i * math.pi / 180
        glVertex2f(100 + 80 * math.cos(angle), 100 + 80 * math.sin(angle))
    glEnd()
    
    # Draw radar grid
    glColor3f(0, 0.5, 0.5)  # Darker cyan
    glBegin(GL_LINES)
    glVertex2f(20, 100)
    glVertex2f(180, 100)
    glVertex2f(100, 20)
    glVertex2f(100, 180)
    glEnd()
    
    # Draw radar sweep line (direction facing)
    glColor3f(0, 1, 0.7)  # Bright cyan
    glBegin(GL_LINES)
    glVertex2f(100, 100)
    glVertex2f(100 + 80 * math.cos(player_rotation * math.pi / 180), 
               100 + 80 * math.sin(player_rotation * math.pi / 180))
    glEnd()
    
    # Draw enemy blips on radar
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(1, 0.3, 0.3)  # Red for enemies
    for enemy in enemies:
        # Convert enemy position to radar coordinates
        dx = enemy[0] - player_pos[0]
        dy = enemy[1] - player_pos[1]
        # Scale down and rotate to match player's orientation
        distance = math.sqrt(dx*dx + dy*dy) / (BATTLEFIELD_SIZE/2) * 70
        if distance < 80:  # Only show enemies within radar range
            angle = math.atan2(dy, dx) - player_rotation * math.pi / 180
            radar_x = 100 + distance * math.cos(angle)
            radar_y = 100 + distance * math.sin(angle)
            glVertex2f(radar_x, radar_y)
    glEnd()

    # Draw cardinal direction labels (N, S, E, W) around the radar
    # These should rotate with the player's rotation
    directions = ['N', 'E', 'S', 'W']
    for i, label in enumerate(directions):
        # 0 = N, 1 = E, 2 = S, 3 = W
        base_angle = i * 90  # 0, 90, 180, 270
        # Adjust for player rotation (so N always points to world north)
        angle = (base_angle - player_rotation) * math.pi / 180
        label_x = 100 + 90 * math.cos(angle) - 8  # -8 to center text
        label_y = 100 + 90 * math.sin(angle) - 8
        draw_text(label_x, label_y, label)

    # Reset matrix state
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glPopMatrix()

def draw_hud():
    """Draw the heads-up display (HUD) without health bar"""
    # Speed indicator
    draw_text(10, 750, f"SPEED: {int(player_speed * 200)} KPH")
    
    # Score
    draw_text(10, 720, f"SCORE: {score}")
    
    # Current level
    draw_text(10, 690, f"LEVEL: {current_level}")
    
    # Ammo
    draw_text(800, 750, f"LASERS: {len(bullets)}/50")
    
    # Distance indicator
    if enemies:
        # Find closest enemy
        closest_dist = float('inf')
        for enemy in enemies:
            dx = enemy[0] - player_pos[0]
            dy = enemy[1] - player_pos[1]
            dz = enemy[2] - player_pos[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < closest_dist:
                closest_dist = dist
        draw_text(800, 720, f"TARGET: {int(closest_dist)} M")
    
    # Level objectives
    level_data = LEVEL_CONFIG.get(current_level, LEVEL_CONFIG[1])
    next_level_score = level_data["next_level_score"]
    
    if current_level < len(LEVEL_CONFIG):
        progress = min(1.0, score / next_level_score)
        draw_text(400, 750, f"LEVEL PROGRESS: {int(progress * 100)}%")
        draw_text(400, 720, f"NEXT LEVEL: {next_level_score - score} PTS")
    else:
        draw_text(400, 750, "FINAL LEVEL")

def draw_health_bar():
    """Draw an improved health bar with numeric indicators and segments"""
    # Set up orthographic projection for 2D overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Ensure player_health is properly clamped
    clamped_health = max(0, min(player_health, max_player_health))
    health_percent = clamped_health / max_player_health
    
    # Dynamic health bar color based on health percentage
    if health_percent > 0.6:  # More than 60% health - green
        bar_color = (0.0, 1.0, 0.0)
    elif health_percent > 0.3:  # Between 30% and 60% health - yellow
        bar_color = (1.0, 1.0, 0.0)
    else:  # Less than 30% health - red
        bar_color = (1.0, 0.0, 0.0)
    
    # Health bar background with border effect
    glColor3f(0.2, 0.2, 0.2)  # Dark gray background
    glBegin(GL_QUADS)
    glVertex2f(8, 648)
    glVertex2f(212, 648)
    glVertex2f(212, 672)
    glVertex2f(8, 672)
    glEnd()
    
    # Health bar border
    glColor3f(0.5, 0.5, 0.5)  # Medium gray border
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(10, 650)
    glVertex2f(210, 650)
    glVertex2f(210, 670)
    glVertex2f(10, 670)
    glEnd()
    glLineWidth(1.0)
    
    # Draw health bar with segments for better visualization
    if health_percent > 0:
        # Number of segments in the health bar
        num_segments = 10
        segment_width = 200 / num_segments
        filled_segments = int(health_percent * num_segments)
        
        # Draw filled segments
        for i in range(filled_segments):
            # Calculate segment position
            x_start = 10 + i * segment_width
            
            # Draw segment with a small gap between segments
            gap = 1
            glColor3f(*bar_color)
            glBegin(GL_QUADS)
            glVertex2f(x_start, 652)
            glVertex2f(x_start + segment_width - gap, 652)
            glVertex2f(x_start + segment_width - gap, 668)
            glVertex2f(x_start, 668)
            glEnd()
        
        # Add highlight effect to filled segments
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(1.0, 1.0, 1.0, 0.3)  # White highlight with 30% opacity
        glBegin(GL_QUADS)
        glVertex2f(10, 664)  # Top half of the bar
        glVertex2f(10 + filled_segments * segment_width, 664)
        glVertex2f(10 + filled_segments * segment_width, 668)
        glVertex2f(10, 668)
        glEnd()
        glDisable(GL_BLEND)
    
    # Draw health numbers with shadow effect for better visibility
    # Shadow
    glColor3f(0.0, 0.0, 0.0)
    draw_text(14, 651, f"{int(clamped_health)} / {max_player_health}", GLUT_BITMAP_9_BY_15)
    
    # Actual text (color varies based on health)
    glColor3f(*bar_color)
    draw_text(15, 652, f"{int(clamped_health)} / {max_player_health}", GLUT_BITMAP_9_BY_15)
    
    # Add warning indicator for low health (below 30%)
    if health_percent <= 0.3 and health_percent > 0:
        # Make the warning blink using a sine wave based on time
        blink_rate = math.sin(glutGet(GLUT_ELAPSED_TIME) / 100.0) * 0.5 + 0.5
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(1.0, 0.0, 0.0, blink_rate * 0.8)  # Blinking red
        
        # Draw warning icon
        glBegin(GL_TRIANGLES)
        glVertex2f(222, 650)
        glVertex2f(232, 670)
        glVertex2f(212, 670)
        glEnd()
        
        # Draw exclamation mark inside warning
        glColor4f(1.0, 1.0, 1.0, blink_rate)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(222, 655)
        glVertex2f(222, 665)
        glEnd()
        glBegin(GL_POINTS)
        glVertex2f(222, 667)
        glEnd()
        glLineWidth(1.0)
        glDisable(GL_BLEND)
    
    # Damage indicator effect (flashing red when recently damaged)
    if damage_cooldown > 0:
        # Pulsing alpha based on cooldown
        alpha = 0.7 * (damage_cooldown / 30.0)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 0.0, 0.0, alpha)
        
        # Full screen red flash effect
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(1000, 0)
        glVertex2f(1000, 800)
        glVertex2f(0, 800)
        glEnd()
        
        glDisable(GL_BLEND)
    
    # Reset matrix state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_battlefield():
    """Draw the space battlefield with animated floor grid"""
    # Draw a starfield background
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1, 1, 1)  # White stars
    for i in range(500):
        x = random.uniform(-BATTLEFIELD_SIZE*2, BATTLEFIELD_SIZE*2)
        y = random.uniform(-BATTLEFIELD_SIZE*2, BATTLEFIELD_SIZE*2)
        z = random.uniform(-BATTLEFIELD_SIZE, 0)  # Stars below the battlefield
        glVertex3f(x, y, z)
    glEnd()
    
    # Draw a nebula effect using transparent quads
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBegin(GL_QUADS)
    for i in range(20):
        x = random.uniform(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE)
        y = random.uniform(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE)
        z = random.uniform(-500, -100)
        size = random.uniform(100, 300)
        
        r = random.uniform(0, 0.5)
        g = random.uniform(0, 0.5)
        b = random.uniform(0.5, 1.0)
        a = 0.2  # Alpha (transparency)
        
        glColor4f(r, g, b, a)
        glVertex3f(x - size, y - size, z)
        glVertex3f(x + size, y - size, z)
        glVertex3f(x + size, y + size, z)
        glVertex3f(x - size, y + size, z)
    glEnd()
    
    glDisable(GL_BLEND)
    
    # Draw the animated grid floor
    draw_animated_floor()
    
    # Draw invisible boundary indicators
    draw_battlefield_boundaries()

def draw_animated_floor():
    """Draw an animated grid floor that gives a sense of movement"""
    global grid_offset_x, grid_offset_y
    
    # Calculate grid offsets based on player orientation and speed
    rad = player_rotation * math.pi / 180
    movement_x = math.cos(rad) * grid_animation_speed
    movement_y = math.sin(rad) * grid_animation_speed
    
    # Update grid offsets
    grid_offset_x = (grid_offset_x + movement_x) % grid_line_spacing
    grid_offset_y = (grid_offset_y + movement_y) % grid_line_spacing
    
    glBegin(GL_LINES)
    glColor3f(0.2, 0.4, 0.8)  # Light blue grid
    
    # Draw an extended grid to create motion effect
    # The grid should extend beyond player's view for smooth animation
    grid_size = BATTLEFIELD_SIZE * 2  # Extended grid size
    
    # Draw X-axis lines
    for i in range(-grid_size, grid_size + grid_line_spacing, grid_line_spacing):
        grid_pos = i - grid_offset_x
        glVertex3f(grid_pos, -grid_size, 0)
        glVertex3f(grid_pos, grid_size, 0)
    
    # Draw Y-axis lines
    for i in range(-grid_size, grid_size + grid_line_spacing, grid_line_spacing):
        grid_pos = i - grid_offset_y
        glVertex3f(-grid_size, grid_pos, 0)
        glVertex3f(grid_size, grid_pos, 0)
    
    glEnd()
    
    # Add additional "flowing" lines for enhanced speed effect
    draw_flow_lines()

def draw_flow_lines():
    """Draw flowing lines that enhance the speed effect"""
    # Number of flow lines
    num_flow_lines = 50
    
    # Flow line parameters
    flow_line_length = 100
    flow_line_width = 2
    
    # Set up flow line rendering
    glLineWidth(flow_line_width)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBegin(GL_LINES)
    
    for i in range(num_flow_lines):
        # Random position within battlefield
        x = random.uniform(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE)
        y = random.uniform(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE)
        
        # Calculate position relative to player
        dx = x - player_pos[0]
        dy = y - player_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Only draw lines in front of player for better effect
        rad = player_rotation * math.pi / 180
        forward_x = math.cos(rad)
        forward_y = math.sin(rad)
        
        # Check if line is in front of player
        dot_product = dx * forward_x + dy * forward_y
        
        # Fade alpha based on distance
        alpha = max(0, 1 - distance / BATTLEFIELD_SIZE)
        
        if dot_product > 0:
            # Line is in front, make it flow toward the player
            glColor4f(0.0, 0.7, 1.0, alpha * 0.7)  # Blue line with alpha
            
            # Starting point
            glVertex3f(x, y, 10)
            
            # Endpoint (flow toward player's view direction)
            end_x = x - forward_x * flow_line_length
            end_y = y - forward_y * flow_line_length
            glVertex3f(end_x, end_y, 10)
    
    glEnd()
    
    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)
    glLineWidth(1)  # Reset line width

def draw_player():
    """Draw the player's spaceship"""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_rotation, 0, 0, 1)  # Rotate around z-axis
    draw_spaceship(True)
    glPopMatrix()

def draw_enemies():
    """Draw enemy spaceships with their health bars"""
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy[0], enemy[1], enemy[2])
        glRotatef(enemy[3], 0, 0, 1)  # Rotate around z-axis
        
        # Draw appropriate enemy ship based on enemy type (element at index 4)
        draw_enemy_ship(enemy[4])
        
        # Draw health bar above enemy
        # Get max health for this enemy type
        max_health = ENEMY_TYPES[enemy[4]]["health"]
        health_percent = enemy[5] / max_health
        
        glTranslatef(0, 0, 30)  # Position above ship
        
        # Draw health bar background (dark red)
        glColor3f(0.3, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-20, -3, 0)
        glVertex3f(20, -3, 0)
        glVertex3f(20, 3, 0)
        glVertex3f(-20, 3, 0)
        glEnd()
        
        # Draw health bar (green to red based on health percentage)
        r = min(1.0, 2.0 - 2.0 * health_percent)  # Red increases as health decreases
        g = min(1.0, 2.0 * health_percent)        # Green increases as health increases
        glColor3f(r, g, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-20, -3, 0.1)
        glVertex3f(-20 + 40 * health_percent, -3, 0.1)
        glVertex3f(-20 + 40 * health_percent, 3, 0.1)
        glVertex3f(-20, 3, 0.1)
        glEnd()
        
        glPopMatrix()

def draw_bullets():
    """Draw laser beams"""
    for bullet in bullets:
        glPushMatrix()
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glRotatef(bullet[3], 0, 0, 1)  # Rotate to match firing direction
        draw_laser_beam()
        glPopMatrix()

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement and actions
    """
    global player_pos, player_rotation, player_speed, player_boost_speed, bullets, game_over, camera_mode, grid_animation_speed, camera_distance
    global moving_forward, moving_backward, thruster_glow_intensity
    
    if key == b'\x1b':  # ESC key
        sys.exit(0)
        
    if game_over:
        if key == b'r':  # Reset game
            reset_game()
        return
        
    # Move forward (W key) with increased speed
    if key == b'w':
        rad = player_rotation * math.pi / 180
        # Using enhanced speed for forward movement
        movement_speed = player_boost_speed
        # Calculate new position
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        # Check battlefield boundaries before moving
        if abs(new_x) < BATTLEFIELD_SIZE and abs(new_y) < BATTLEFIELD_SIZE:
            player_pos[0] = new_x
            player_pos[1] = new_y
            moving_forward = True
            moving_backward = False
            thruster_glow_intensity = 0.8  # Full thruster effect
        else:
            # If would hit boundary, still allow partial movement (slide along boundary)
            if abs(new_x) < BATTLEFIELD_SIZE:
                player_pos[0] = new_x
            if abs(new_y) < BATTLEFIELD_SIZE:
                player_pos[1] = new_y
            moving_forward = True
            thruster_glow_intensity = 0.5  # Reduced thruster effect at boundary
    
    # Move backward (S key) with increased speed
    if key == b's':
        rad = player_rotation * math.pi / 180
        # Same speed for backward movement
        movement_speed = player_speed
        # Calculate new position
        new_x = player_pos[0] - math.cos(rad) * movement_speed
        new_y = player_pos[1] - math.sin(rad) * movement_speed
        
        # Check battlefield boundaries before moving
        if abs(new_x) < BATTLEFIELD_SIZE and abs(new_y) < BATTLEFIELD_SIZE:
            player_pos[0] = new_x
            player_pos[1] = new_y
            moving_backward = True
            moving_forward = False
            thruster_glow_intensity = 0.4  # Medium thruster effect for reverse
        else:
            # If would hit boundary, still allow partial movement (slide along boundary)
            if abs(new_x) < BATTLEFIELD_SIZE:
                player_pos[0] = new_x
            if abs(new_y) < BATTLEFIELD_SIZE:
                player_pos[1] = new_y
            moving_backward = True
            thruster_glow_intensity = 0.2  # Reduced thruster effect at boundary
    
    # Reset movement flags when releasing W or S
    if key not in (b'w', b's'):
        moving_forward = False
        moving_backward = False
    
    # Strafe left (A key) with increased speed
    if key == b'a':
        rad = (player_rotation + 90) * math.pi / 180  # 90 degrees to the left of player orientation
        # Enhanced speed for strafing
        movement_speed = player_boost_speed
        # Calculate new position
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        # Check battlefield boundaries before moving
        if abs(new_x) < BATTLEFIELD_SIZE and abs(new_y) < BATTLEFIELD_SIZE:
            player_pos[0] = new_x
            player_pos[1] = new_y
        else:
            # If would hit boundary, still allow partial movement (slide along boundary)
            if abs(new_x) < BATTLEFIELD_SIZE:
                player_pos[0] = new_x
            if abs(new_y) < BATTLEFIELD_SIZE:
                player_pos[1] = new_y
    
    # Strafe right (D key) with increased speed
    if key == b'd':
        rad = (player_rotation - 90) * math.pi / 180  # 90 degrees to the right of player orientation
        # Enhanced speed for strafing
        movement_speed = player_boost_speed
        # Calculate new position
        new_x = player_pos[0] + math.cos(rad) * movement_speed
        new_y = player_pos[1] + math.sin(rad) * movement_speed
        
        # Check battlefield boundaries before moving
        if abs(new_x) < BATTLEFIELD_SIZE and abs(new_y) < BATTLEFIELD_SIZE:
            player_pos[0] = new_x
            player_pos[1] = new_y
        else:
            # If would hit boundary, still allow partial movement (slide along boundary)
            if abs(new_x) < BATTLEFIELD_SIZE:
                player_pos[0] = new_x
            if abs(new_y) < BATTLEFIELD_SIZE:
                player_pos[1] = new_y
    
    # Rise (R key) with increased speed - add height limit
    if key == b'r':
        new_z = player_pos[2] + player_speed
        # Limit maximum height to prevent leaving the battlefield vertically
        if new_z < 500:  # Maximum height
            player_pos[2] = new_z
    
    # Descend (F key) with increased speed - add minimum height
    if key == b'f':
        new_z = player_pos[2] - player_speed
        # Prevent going below a minimum height
        if new_z > 20:  # Minimum height above battlefield floor
            player_pos[2] = new_z
    
    # Toggle camera mode (C key)
    if key == b'c':
        camera_mode = 1 - camera_mode  # Toggle between 0 and 1
        
    # Fire lasers (Shift key)
    if key in (b'\x10', b' '):  # Left shift (0x10) or spacebar as alternative
        if len(bullets) < 50:  # Limit number of laser beams
            rad = player_rotation * math.pi / 180
            offsets = [
                (-18, 18),   # Far left
                (-9, 9),     # Left-center
                (0, 0),      # Center
                (9, -9),     # Right-center
                (18, -18)    # Far right
            ]
            for offset_x, offset_y in offsets:
                laser = [
                    player_pos[0] + 30 * math.cos(rad) + offset_x * math.sin(rad),
                    player_pos[1] + 30 * math.sin(rad) + offset_y * math.cos(rad),
                    player_pos[2],
                    player_rotation,
                    player_boost_speed + 20,  # Faster bullet speed based on boosted speed
                    200  # Increased lifetime for longer range
                ]
                bullets.append(laser)

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for player rotation and camera distance
    """
    global player_rotation, camera_distance
    
    # Rotate left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        player_rotation = (player_rotation + 5) % 360
    
    # Rotate right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        player_rotation = (player_rotation - 5) % 360
    
    # Move camera farther (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_distance = min(camera_distance + 10, 1000)  # Set a reasonable max distance
    
    # Move camera closer (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_distance = max(camera_distance - 10, 50)  # Set a reasonable min distance

def mouseListener(button, state, x, y):
    """
    Handles mouse inputs (no longer used for firing)
    """
    # Mouse click functionality moved to keyboard handler
    pass

def update_enemies():
    """Update enemy behavior and movement"""
    global enemies, enemy_bullets
    
    for enemy in enemies:
        # Get enemy type and characteristics
        enemy_type = enemy[4]
        type_data = ENEMY_TYPES[enemy_type]
        
        # Calculate distance to player
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        dz = player_pos[2] - enemy[2]
        distance_to_player = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Calculate angle to player in degrees
        angle_to_player = math.degrees(math.atan2(dy, dx)) % 360
        
        # Different behaviors based on distance to player
        follow_distance = type_data["follow_distance"]
        firing_distance = type_data["firing_distance"]
        
        if distance_to_player < follow_distance:
            # Player is within detection range - follow player
            
            # Gradually rotate towards player
            # Find the shortest way to rotate to the player
            angle_diff = (angle_to_player - enemy[3]) % 360
            if angle_diff > 180:
                angle_diff -= 360
                
            # Set rotation speed based on enemy type (higher types rotate faster)
            rotation_speed = 2 + enemy_type * 0.5
            
            # Limit the rotation to the rotation speed
            if angle_diff > rotation_speed:
                enemy[3] = (enemy[3] + rotation_speed) % 360
            elif angle_diff < -rotation_speed:
                enemy[3] = (enemy[3] - rotation_speed) % 360
            else:
                # We're close enough, set exact angle
                enemy[3] = angle_to_player
            
            # Move towards player if not too close
            min_distance = 200  # Don't get closer than this
            
            if distance_to_player > min_distance:
                # Speed varies by enemy type
                speed = type_data["speed"]
                
                # Calculate actual direction to player (not just current facing)
                actual_rad = math.atan2(dy, dx)
                # Weighted average between actual direction and current direction
                # The higher the weight (0.7), the more directly enemies will chase
                weight = 0.7
                move_rad = actual_rad * weight + (enemy[3] * math.pi / 180) * (1 - weight)
                
                # Move more directly toward player
                enemy[0] += math.cos(move_rad) * speed
                enemy[1] += math.sin(move_rad) * speed
                
                # Adjust height to be closer to player's height
                if enemy[2] < player_pos[2] - 20:
                    enemy[2] += 1
                elif enemy[2] > player_pos[2] + 20:
                    enemy[2] -= 1
            
            # Fire at player if within firing range
            if distance_to_player < firing_distance:
                # Decrease firing cooldown
                enemy[6] -= 1
                
                if enemy[6] <= 0:
                    # Reset cooldown based on firing rate
                    enemy[6] = type_data["firing_rate"]
                    
                    # Fire bullet at player
                    # Calculate a slight lead to aim where the player will be
                    lead_factor = 0.5  # Higher value = more lead
                    player_vel_x = 0
                    player_vel_y = 0
                    
                    # Simple prediction based on player orientation
                    if moving_forward:
                        rad = player_rotation * math.pi / 180
                        player_vel_x = math.cos(rad) * player_speed * lead_factor
                        player_vel_y = math.sin(rad) * player_speed * lead_factor
                    
                    # Calculate aim point (leading the target)
                    aim_x = player_pos[0] + player_vel_x
                    aim_y = player_pos[1] + player_vel_y
                    
                    # Calculate angle to aim point
                    dx_aim = aim_x - enemy[0]
                    dy_aim = aim_y - enemy[1]
                    aim_angle = math.degrees(math.atan2(dy_aim, dx_aim)) % 360
                    
                    # Create enemy bullet
                    bullet_speed = type_data["bullet_speed"]
                    bullet_lifetime = type_data["bullet_lifetime"]
                    
                    # Add slight randomness to make it less perfect
                    aim_angle += random.uniform(-3, 3)
                    
                    # Fire from the front of the enemy ship
                    rad = aim_angle * math.pi / 180
                    bullet_x = enemy[0] + 30 * math.cos(rad)
                    bullet_y = enemy[1] + 30 * math.sin(rad)
                    
                    enemy_bullets.append([
                        bullet_x,           # x
                        bullet_y,           # y
                        enemy[2],           # z (same height as enemy)
                        aim_angle,          # rotation (aiming at player)
                        bullet_speed,       # speed
                        bullet_lifetime,    # lifetime
                        enemy_type          # store enemy type for damage calculation
                    ])
        else:
            # Player out of range - maintain patrol pattern or random movement
            # Simple AI - randomly change direction and move forward
            if random.random() < 0.02:  # 2% chance to change direction
                enemy[3] = (enemy[3] + random.uniform(-30, 30)) % 360
            
            # Move forward in current direction
            rad = enemy[3] * math.pi / 180
            speed = type_data["speed"] * 0.6  # Slower speed when patrolling
            enemy[0] += math.cos(rad) * speed
            enemy[1] += math.sin(rad) * speed
        
        # Keep enemies within battlefield bounds
        enemy[0] = max(min(enemy[0], BATTLEFIELD_SIZE), -BATTLEFIELD_SIZE)
        enemy[1] = max(min(enemy[1], BATTLEFIELD_SIZE), -BATTLEFIELD_SIZE)
        
        # Check for collision with player
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        dz = player_pos[2] - enemy[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 50:  # Collision with player!
            # Apply damage to player based on enemy type if not in cooldown
            if damage_cooldown <= 0:
                damage = type_data["damage"] * 2  # Double damage for collisions
                player_health = max(0, player_health - damage)  # Ensure health doesn't go below 0
                damage_cooldown = 30  # Set damage cooldown
                
                # Check if player is destroyed
                if player_health <= 0:
                    player_health = 0
                    game_over = True

def update_game():
    """
    Update game state - move bullets, check collisions, enemy AI, etc.
    """
    global bullets, enemy_bullets, enemies, score, game_over, thruster_glow_intensity, thruster_particles
    global player_health, damage_cooldown, current_level
    
    # Gradually decrease thruster effect when not moving (neither forward nor backward)
    if not moving_forward and not moving_backward:
        thruster_glow_intensity = max(0.0, thruster_glow_intensity - 0.05)
    
    # Update thruster particles only when thrusters are active and not moving backward
    if thruster_glow_intensity > 0 and not moving_backward:
        update_thruster_particles()
    
    # Decrease damage cooldown timer if player recently took damage
    if damage_cooldown > 0:
        damage_cooldown -= 1
    
    # Update player bullets
    for bullet in bullets[:]:  # Use a copy for safe removal
        # Move bullet forward based on its direction
        rad = bullet[3] * math.pi / 180
        bullet[0] += math.cos(rad) * bullet[4]
        bullet[1] += math.sin(rad) * bullet[4]
        
        # Decrease lifetime
        bullet[5] -= 1
        
        # Remove bullet if lifetime expired
        if bullet[5] <= 0:
            bullets.remove(bullet)
            continue
        
        # Check for collisions with enemies
        for enemy in enemies[:]:  # Use a copy for safe removal
            dx = bullet[0] - enemy[0]
            dy = bullet[1] - enemy[1]
            dz = bullet[2] - enemy[2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if distance < 30:  # Hit!
                if bullet in bullets:  # Ensure bullet still exists
                    bullets.remove(bullet)
                
                # Get enemy type and reduce health
                enemy_type = enemy[4]
                enemy[5] -= 50  # Damage amount from player bullets
                
                # Check if enemy is destroyed
                if enemy[5] <= 0:
                    # Get score value for this enemy type
                    score_value = ENEMY_TYPES[enemy_type]["score_value"]
                    score += score_value
                    enemies.remove(enemy)
                    
                    # Spawn a new enemy of appropriate type for current level
                    level_data = LEVEL_CONFIG.get(current_level, LEVEL_CONFIG[1])
                    enemy_types = level_data["enemy_types"]
                    new_enemy_type = random.choice(enemy_types)
                    
                    # Get enemy type data
                    type_data = ENEMY_TYPES[new_enemy_type]
                    
                    enemies.append([
                        random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                        random.uniform(-BATTLEFIELD_SIZE/2, BATTLEFIELD_SIZE/2),
                        random.uniform(100, 500),
                        random.uniform(0, 360),
                        new_enemy_type,                  # enemy type
                        type_data["health"],             # health
                        0,                               # firing cooldown
                        0                                # behavior state
                    ])
                
                # We've processed this hit, move on to next bullet
                break
    
    # Update enemy bullets
    for bullet in enemy_bullets[:]:  # Use a copy for safe removal
        # Move bullet forward based on its direction
        rad = bullet[3] * math.pi / 180
        bullet[0] += math.cos(rad) * bullet[4]
        bullet[1] += math.sin(rad) * bullet[4]
        
        # Decrease lifetime
        bullet[5] -= 1
        
        # Remove bullet if lifetime expired
        if bullet[5] <= 0:
            enemy_bullets.remove(bullet)
            continue
        
        # Check for collision with player
        dx = bullet[0] - player_pos[0]
        dy = bullet[1] - player_pos[1]
        dz = bullet[2] - player_pos[2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if distance < 40:  # Hit player!
            if bullet in enemy_bullets:  # Ensure bullet still exists
                enemy_bullets.remove(bullet)
            
            # Only take damage if not in cooldown period
            if damage_cooldown <= 0:
                # Get enemy type to determine damage
                enemy_type = bullet[6]  # Enemy type stored in bullet
                damage = ENEMY_TYPES[enemy_type]["damage"]
                
                # Apply damage to player with explicit clamping to prevent negative health
                player_health = max(0, player_health - damage)
                damage_cooldown = 30  # Set damage cooldown (half a second at 60 FPS)
                
                # Check if player is destroyed
                if player_health <= 0:
                    player_health = 0  # Ensure health doesn't go negative for display purposes
                    game_over = True
    
    # Update enemy behavior
    update_enemies()
    
    # Check for level advancement
    if not game_over:
        check_level_advancement()

def check_level_advancement():
    """Check if player should advance to the next level"""
    global current_level, score
    
    # Get current level configuration
    level_data = LEVEL_CONFIG.get(current_level, LEVEL_CONFIG[1])
    
    # Check if score meets the threshold for next level
    if score >= level_data["next_level_score"] and current_level < len(LEVEL_CONFIG):
        # Advance to next level
        current_level += 1
        
        # Clear bullets
        bullets.clear()
        enemy_bullets.clear()
        
        # Re-initialize enemies for the new level
        initialize_enemies()
        
        # Add bonus health for level advancement (25% of max health, but don't exceed max)
        global player_health, max_player_health
        bonus_health = max_player_health * 0.25
        player_health = min(player_health + bonus_health, max_player_health)

def update_thruster_particles():
    """Update thruster particle effects"""
    global thruster_particles
    
    # Remove expired particles
    thruster_particles = [p for p in thruster_particles if p[3] > 0]
    
    # Update existing particles
    for particle in thruster_particles:
        # Move particle
        particle[0] += particle[4]
        particle[1] += particle[5]
        particle[2] += particle[6]
        
        # Decrease lifetime
        particle[3] -= 1
    
    # Add new particles only when moving forward or idle with thruster glow
    if thruster_glow_intensity > 0:
        rad = player_rotation * math.pi / 180
        
        # Central thruster particle generation
        # Calculate particle position relative to central engine
        x = player_pos[0] - 65 * math.cos(rad) - 15 * math.cos(rad)
        y = player_pos[1] - 65 * math.sin(rad) - 15 * math.sin(rad)
        
        # Add multiple particles per frame for the central thruster
        for _ in range(int(4 * thruster_glow_intensity)):
            # Random spread around central engine
            offset_y = random.uniform(-10, 10)
            offset_z = random.uniform(-10, 10)
            
            z = player_pos[2] + offset_z
            y_adjusted = y + offset_y * 0.5  # Reduce horizontal spread
            
            # Random velocity components
            vx = -math.cos(rad) * random.uniform(3, 6)  # Slightly slower particles
            vy = -math.sin(rad) * random.uniform(3, 6) + offset_y * 0.2
            vz = random.uniform(-0.8, 0.8) + offset_z * 0.1
            
            # Add particle with longer lifetime for the larger thruster
            lifetime = int(random.uniform(20, 35) * thruster_glow_intensity)
            thruster_particles.append([x, y_adjusted, z, lifetime, vx, vy, vz])
        
        # Side thrusters (smaller particles)
        for y_offset in [-18, 18]:
            side_x = player_pos[0] - 50 * math.cos(rad) - 8 * math.cos(rad)
            side_y = player_pos[1] - 50 * math.sin(rad) - 8 * math.sin(rad)
            side_y += y_offset * math.cos(rad * math.pi / 180)  # Adjust for ship rotation
            side_x += y_offset * math.sin(rad * math.pi / 180)
            
            if random.random() < 0.3 * thruster_glow_intensity:
                vx = -math.cos(rad) * random.uniform(1, 3)
                vy = -math.sin(rad) * random.uniform(1, 3)
                vz = random.uniform(-0.3, 0.3)
                
                thruster_particles.append([side_x, side_y, player_pos[2], 15, vx, vy, vz])

def reset_game():
    """Reset game state for a new game"""
    global player_pos, player_rotation, player_speed, player_boost_speed 
    global enemies, bullets, enemy_bullets, score, game_over
    global moving_forward, moving_backward, thruster_glow_intensity, thruster_particles
    global player_health, max_player_health, damage_cooldown, current_level
    
    player_pos = [0, 0, 50]
    player_rotation = 90  # Start at 90 degrees
    player_speed = 10  # Reset to increased speed
    player_boost_speed = 15  # Reset boost speed
    player_health = max_player_health  # Reset to full health
    damage_cooldown = 0
    current_level = 1  # Start at level 1
    enemies = []
    bullets = []
    enemy_bullets = []
    score = 0
    game_over = False
    moving_forward = False
    moving_backward = False
    thruster_glow_intensity = 0.0
    thruster_particles = []
    
    # Initialize enemies based on level 1 configuration
    initialize_enemies()

def setupCamera():
    """
    Configures the camera's projection and view settings.
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == 0:  # Third-person view
        # Position camera behind and above player
        rad = (player_rotation + 180) * math.pi / 180  # Behind player
        camera_x = player_pos[0] + camera_distance * math.cos(rad)
        camera_y = player_pos[1] + camera_distance * math.sin(rad)
        camera_z = player_pos[2] + 100  # Above player
        
        # Look at player
        gluLookAt(camera_x, camera_y, camera_z,  # Camera position
                player_pos[0], player_pos[1], player_pos[2],  # Look at player
                0, 0, 1)  # Up vector (z-axis)
    else:  # First-person/cockpit view
        # Position camera at player position
        rad = player_rotation * math.pi / 180
        look_x = player_pos[0] + 100 * math.cos(rad)
        look_y = player_pos[1] + 100 * math.sin(rad)
        
        gluLookAt(player_pos[0], player_pos[1], player_pos[2] + 10,  # Camera at player
                look_x, look_y, player_pos[2],  # Look forward
                0, 0, 1)  # Up vector

def idle():
    """
    Idle function for continuous updates
    """
    if not game_over:
        update_game()
    glutPostRedisplay()

def draw_game_over_screen():
    """Draw a detailed game over screen with instructions"""
    # Set up orthographic projection for 2D overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Semi-transparent background
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.7)  # Black with 70% opacity
    glBegin(GL_QUADS)
    glVertex2f(250, 250)
    glVertex2f(750, 250)
    glVertex2f(750, 550)
    glVertex2f(250, 550)
    glEnd()
    glDisable(GL_BLEND)
    
    # Border for game over box
    glColor3f(1.0, 0.0, 0.0)  # Red border
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(250, 250)
    glVertex2f(750, 250)
    glVertex2f(750, 550)
    glVertex2f(250, 550)
    glEnd()
    glLineWidth(1.0)
    
    # Game over title
    glColor3f(1.0, 0.0, 0.0)  # Red color for "GAME OVER"
    draw_text(400, 500, "GAME OVER", GLUT_BITMAP_HELVETICA_18)
    
    # Final score
    glColor3f(1.0, 1.0, 0.0)  # Yellow for score
    draw_text(350, 450, f"FINAL SCORE: {score}", GLUT_BITMAP_HELVETICA_18)
    draw_text(350, 420, f"LEVEL REACHED: {current_level}", GLUT_BITMAP_HELVETICA_18)
    
    # Instructions
    glColor3f(0.0, 1.0, 1.0)  # Cyan for instructions
    draw_text(350, 370, "Press 'R' to restart game", GLUT_BITMAP_HELVETICA_18)
    draw_text(350, 340, "Press 'ESC' to exit", GLUT_BITMAP_HELVETICA_18)
    
    # Game tips
    glColor3f(0.0, 1.0, 0.5)  # Green-cyan for tips
    draw_text(340, 300, "TIP: Use WASD to move, SPACE to fire lasers", GLUT_BITMAP_HELVETICA_12)
    draw_text(340, 280, "TIP: Press C to toggle camera views", GLUT_BITMAP_HELVETICA_12)
    
    # Reset matrix state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_first_person_hud():
    """Draw first-person HUD elements with position and orientation data"""
    # Only show if in first-person/cockpit view
    if camera_mode != 1:
        return
    
    # Set up orthographic projection for 2D overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw a cockpit-style HUD frame
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw targeting reticle in center of screen
    glColor4f(0.0, 1.0, 1.0, 0.7)  # Cyan with 70% opacity
    
    # Outer circle
    glBegin(GL_LINE_LOOP)
    for i in range(360):
        theta = i * math.pi / 180
        glVertex2f(500 + 30 * math.cos(theta), 400 + 30 * math.sin(theta))
    glEnd()
    
    # Inner circle
    glBegin(GL_LINE_LOOP)
    for i in range(360):
        theta = i * math.pi / 180
        glVertex2f(500 + 5 * math.cos(theta), 400 + 5 * math.sin(theta))
    glEnd()
    
    # Crosshairs
    glBegin(GL_LINES)
    glVertex2f(470, 400)
    glVertex2f(490, 400)
    glVertex2f(510, 400)
    glVertex2f(530, 400)
    glVertex2f(500, 370)
    glVertex2f(500, 390)
    glVertex2f(500, 410)
    glVertex2f(500, 430)
    glEnd()
    
    # Position and orientation data in a fancy digital display box
    # Draw display background box
    glColor4f(0.0, 0.1, 0.2, 0.7)  # Dark blue, semi-transparent
    glBegin(GL_QUADS)
    glVertex2f(720, 50)
    glVertex2f(980, 50)
    glVertex2f(980, 150)
    glVertex2f(720, 150)
    glEnd()
    
    # Draw border for the display
    glColor4f(0.0, 0.8, 1.0, 0.8)  # Bright cyan for border
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(720, 50)
    glVertex2f(980, 50)
    glVertex2f(980, 150)
    glVertex2f(720, 150)
    glEnd()
    glLineWidth(1.0)
    
    # Add a title for the navigation display
    glColor3f(0.0, 1.0, 1.0)
    draw_text(750, 130, "NAVIGATION DATA", GLUT_BITMAP_9_BY_15)
    
    # Add separator line under title
    glBegin(GL_LINES)
    glVertex2f(730, 125)
    glVertex2f(970, 125)
    glEnd()
    
    # Display position coordinates with labels
    glColor3f(0.5, 1.0, 1.0)  # Lighter cyan for labels
    draw_text(730, 110, "POS-X:", GLUT_BITMAP_8_BY_13)
    draw_text(730, 95, "POS-Y:", GLUT_BITMAP_8_BY_13)
    draw_text(730, 80, "POS-Z:", GLUT_BITMAP_8_BY_13)
    draw_text(730, 65, "HDG:", GLUT_BITMAP_8_BY_13)
    
    # Display actual values in a different color
    glColor3f(1.0, 1.0, 0.0)  # Yellow for values
    draw_text(790, 110, f"{int(player_pos[0])}", GLUT_BITMAP_8_BY_13)
    draw_text(790, 95, f"{int(player_pos[1])}", GLUT_BITMAP_8_BY_13)
    draw_text(790, 80, f"{int(player_pos[2])}", GLUT_BITMAP_8_BY_13)
    draw_text(790, 65, f"{int(player_rotation)}\u00B0", GLUT_BITMAP_8_BY_13)  # Degree symbol
    
    # Add a mini-compass on the right side of the display
    compass_center_x = 930
    compass_center_y = 90
    compass_radius = 30
    
    # Compass circle
    glColor4f(0.0, 0.6, 0.8, 0.6)  # Light blue for compass
    glBegin(GL_LINE_LOOP)
    for i in range(360):
        theta = i * math.pi / 180
        glVertex2f(compass_center_x + compass_radius * math.cos(theta),
                 compass_center_y + compass_radius * math.sin(theta))
    glEnd()
    
    # Compass cardinal directions
    directions = [
        ("N", 90), ("E", 0), ("S", 270), ("W", 180),
        ("NE", 45), ("SE", 315), ("SW", 225), ("NW", 135)
    ]
    
    # Draw cardinal markers
    for label, angle in directions:
        # Calculate position on compass
        rad = angle * math.pi / 180
        x = compass_center_x + (compass_radius - 10) * math.cos(rad)
        y = compass_center_y + (compass_radius - 10) * math.sin(rad)
        
        # Only draw the main cardinal directions (N, E, S, W) as text
        if len(label) == 1:
            glColor3f(1.0, 1.0, 0.0)  # Yellow for main directions
            draw_text(x - 4, y - 4, label, GLUT_BITMAP_8_BY_13)
        else:
            # Draw small dots for intermediate directions
            glColor3f(0.7, 0.7, 0.7)  # Grey for minor directions
            glPointSize(3.0)
            glBegin(GL_POINTS)
            glVertex2f(x, y)
            glEnd()
            glPointSize(1.0)
    
    # Current heading indicator
    player_rad = (90 - player_rotation) * math.pi / 180  # Adjust for compass orientation
    glColor3f(1.0, 0.0, 0.0)  # Red for current heading
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex2f(compass_center_x, compass_center_y)
    glVertex2f(compass_center_x + compass_radius * math.cos(player_rad),
             compass_center_y + compass_radius * math.sin(player_rad))
    glEnd()
    glLineWidth(1.0)
    
    # Add speed indicator
    glColor3f(0.0, 1.0, 0.0)  # Green for speed
    speed_text = f"SPEED: {int(player_speed * 200)} KPH"
    if moving_forward:
        speed_text = f"BOOST: {int(player_boost_speed * 200)} KPH"
    draw_text(850, 65, speed_text, GLUT_BITMAP_8_BY_13)
    
    glDisable(GL_BLEND)
    
    # Reset matrix state
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def showScreen():
    """
    Display function to render the game scene
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    # Draw game elements
    draw_battlefield()
    draw_player()
    draw_enemies()
    draw_bullets()
    draw_enemy_bullets()  # Ensure enemy bullets are drawn
    
    # Draw HUD elements (always on top)
    draw_radar()
    draw_hud()
    draw_health_bar()  # Draw improved health bar
    
    # Draw first-person specific HUD elements when in cockpit view
    draw_first_person_hud()
    
    # Show improved game over screen if needed
    if game_over:
        draw_game_over_screen()
    
    glutSwapBuffers()

def draw_battlefield_boundaries():
    """Draw subtle indicators for battlefield boundaries"""
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw subtle boundary walls
    glBegin(GL_QUADS)
    
    # Get player's distance from boundaries
    dist_to_boundary_x = BATTLEFIELD_SIZE - abs(player_pos[0])
    dist_to_boundary_y = BATTLEFIELD_SIZE - abs(player_pos[1])
    
    # Only show boundaries when player is close to them (within 100 units)
    boundary_visibility = 100
    
    # North boundary (positive Y)
    if BATTLEFIELD_SIZE - player_pos[1] < boundary_visibility:
        # Calculate alpha based on proximity to boundary
        alpha = 0.2 * (1.0 - (BATTLEFIELD_SIZE - player_pos[1]) / boundary_visibility)
        glColor4f(0.4, 0.8, 1.0, alpha)  # Cyan-blue, semi-transparent
        glVertex3f(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 500)
        glVertex3f(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 500)
    
    # South boundary (negative Y)
    if BATTLEFIELD_SIZE + player_pos[1] < boundary_visibility:
        # Calculate alpha based on proximity to boundary
        alpha = 0.2 * (1.0 - (BATTLEFIELD_SIZE + player_pos[1]) / boundary_visibility)
        glColor4f(0.4, 0.8, 1.0, alpha)  # Cyan-blue, semi-transparent
        glVertex3f(-BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 500)
        glVertex3f(-BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 500)
    
    # East boundary (positive X)
    if BATTLEFIELD_SIZE - player_pos[0] < boundary_visibility:
        # Calculate alpha based on proximity to boundary
        alpha = 0.2 * (1.0 - (BATTLEFIELD_SIZE - player_pos[0]) / boundary_visibility)
        glColor4f(0.4, 0.8, 1.0, alpha)  # Cyan-blue, semi-transparent
        glVertex3f(BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 0)
        glVertex3f(BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 500)
        glVertex3f(BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 500)
    
    # West boundary (negative X)
    if BATTLEFIELD_SIZE + player_pos[0] < boundary_visibility:
        # Calculate alpha based on proximity to boundary
        alpha = 0.2 * (1.0 - (BATTLEFIELD_SIZE + player_pos[0]) / boundary_visibility)
        glColor4f(0.4, 0.8, 1.0, alpha)  # Cyan-blue, semi-transparent
        glVertex3f(-BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 0)
        glVertex3f(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 0)
        glVertex3f(-BATTLEFIELD_SIZE, BATTLEFIELD_SIZE, 500)
        glVertex3f(-BATTLEFIELD_SIZE, -BATTLEFIELD_SIZE, 500)
        
    glEnd()
    
    glDisable(GL_BLEND)

# Add this code to call initialize_enemies() before entering the main loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Space Shooter")
    
    # Enable depth testing for 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    # Initialize enemies before starting the game loop
    initialize_enemies()  # Add this line
    
    # Register callback functions
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()