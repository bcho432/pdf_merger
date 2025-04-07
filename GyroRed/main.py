import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Define the vertices and edges of a cube
vertices = [
    [1, 1, -1],
    [1, -1, -1],
    [-1, -1, -1],
    [-1, 1, -1],
    [1, 1, 1],
    [1, -1, 1],
    [-1, -1, 1],
    [-1, 1, 1]
]

edges = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 0],
    [4, 5],
    [5, 6],
    [6, 7],
    [7, 4],
    [0, 4],
    [1, 5],
    [2, 6],
    [3, 7]
]

def draw_cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    # Initialize GLFW
    if not glfw.init():
        return
    
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(800, 600, "Rotating Cube", None, None)
    if not window:
        glfw.terminate()
        return
    
    # Make the window's context current
    glfw.make_context_current(window)
    
    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    
    # Main loop
    angle = 0.0
    while not glfw.window_should_close(window):
        # Poll for and process events
        glfw.poll_events()
        
        # Clear the color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 800/600, 0.1, 50.0)
        
        # Set up the modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        
        # Apply rotation
        glRotatef(angle, 1, 1, 1)
        angle += 0.5
        
        # Draw the cube
        draw_cube()
        
        # Swap front and back buffers
        glfw.swap_buffers(window)
    
    # Terminate GLFW
    glfw.terminate()

if __name__ == "__main__":
    main()
