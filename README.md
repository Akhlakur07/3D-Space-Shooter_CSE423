# 🚀 3D Space Shooter

A 3D space combat game built with Python and OpenGL where players pilot a battleship through various levels of increasingly difficult enemy encounters.

![3D Space Shooter](assets/Screenshot%202025-05-03%20023250.png)

## 👨‍🚀 Description

3D Space Shooter is an action-packed space combat game where you control a powerful battleship and engage in intense dogfights with enemy spacecraft. Navigate through an expansive battlefield, take down enemies, avoid enemy fire, and ultimately defeat the final boss to win the game.

## 🌌 Features

- **3D Combat:** Fully 3D rendered space environment with detailed spacecraft models
- **Progressive Difficulty:** 4 levels with increasingly challenging enemies
- **Enemy Types:** Multiple enemy types with unique characteristics and abilities
- **Power-ups:** Shields and missiles for tactical advantages
- **Combo System:** Chain enemy kills for score multipliers
- **Dynamic HUD:** Real-time display of health, score, shields, and radar
- **Camera Modes:** Toggle between third-person and cockpit views

## 🕹️ Controls

### Movement

- **W:** Move forward
- **S:** Move backward
- **A:** Strafe left
- **D:** Strafe right
- **Left/Right Arrow Keys:** Rotate ship
- **R:** Ascend
- **F:** Descend
- **Up/Down Arrow Keys:** Adjust camera distance

### Combat & Abilities

- **Spacebar:** Fire lasers
- **M:** Launch missile (one per level)
- **P:** Activate shield (once per game)

### Game Controls

- **L:** Toggle camera mode
- **C:** Toggle cheat mode
- **R:** Restart game (when game over)
- **UI Buttons:** Pause/resume and restart

## 🎮 Gameplay

The game consists of 4 progressive levels:

1. **Level 1:** Standard red enemy ships
2. **Level 2:** Introduction of stronger golden enemy ships
3. **Level 3:** Appearance of powerful black-red enemy ships
4. **Level 4:** Final boss battle with supporting enemy ships

Advance through levels by gaining experience points from destroying enemy ships. Watch your health and use shields and missiles strategically. Maintain kill combos to increase your score multiplier.

## 📷 Screenshots

### Main Gameplay

![Gameplay Screenshot](assets/Screenshot%202025-05-03%20022423.png)
_Spaceship and the game arena_

### Advanced Combat

![Combat Screenshot](assets/Screenshot%202025-05-03%20022840.png)
_Player using lasers against multiple enemy ships_

### Boss Battle

![Boss Battle Screenshot](assets/Screenshot%202025-05-03%20022953.png)
_Final boss encounter_

## Requirements ➡️

- Python 3
- PyOpenGL
- PyOpenGL-accelerate
- GLUT/FreeGLUT

## Installation 🖥️

1. Clone the repository:

   ```
   git clone https://github.com/Akhlakur07/3D-Space-Shooter_CSE423.git
   cd 3d-space-shooter
   ```

2. Install the required packages:

   ```
   pip install PyOpenGL PyOpenGL-accelerate
   ```

3. Install GLUT/FreeGLUT:

   - **Windows:** Download FreeGLUT from [here](http://freeglut.sourceforge.net/) and follow installation instructions
   - **macOS:** `brew install freeglut`
   - **Linux:** `sudo apt-get install freeglut3-dev`

4. Run the game:
   ```
   python main.py
   ```
