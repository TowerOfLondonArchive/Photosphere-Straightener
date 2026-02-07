import sys
import os
import glob
import subprocess

from OpenGL.GL import (
    glGenTextures,
    glBindTexture,
    glTexParameteri,
    glTexImage2D,
    glEnable,
    glDisable,
    glClear,
    glBegin,
    glEnd,
    glLoadIdentity,
    glRotatef,
    glViewport,
    glMatrixMode,
    glClearColor,
    glColor3f,
    glPushMatrix,
    glOrtho,
    glLineWidth,
    glVertex2f,
    glPopMatrix,
    glDeleteTextures,
    GL_LINES,
    GL_TEXTURE_2D,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_MAG_FILTER,
    GL_LINEAR,
    GL_RGB,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_PROJECTION,
    GL_MODELVIEW,
    GL_DEPTH_TEST,
    GL_TRUE,
    GL_UNSIGNED_BYTE,
)
from OpenGL.GLU import (
    gluNewQuadric,
    gluQuadricTexture,
    gluQuadricOrientation,
    GLU_INSIDE,
    gluSphere,
    gluDeleteQuadric,
    gluPerspective,
)
from OpenGL.GLUT import (
    glutSwapBuffers,
    glutPostRedisplay,
    glutInit,
    glutInitDisplayMode,
    glutInitWindowSize,
    glutCreateWindow,
    glutDisplayFunc,
    glutReshapeFunc,
    glutMouseFunc,
    glutKeyboardFunc,
    glutMotionFunc,
    glutMainLoop,
    glutGet,
    glutWMCloseFunc,
    GLUT_LEFT_BUTTON,
    GLUT_DOWN,
    GLUT_DOUBLE,
    GLUT_RGB,
    GLUT_DEPTH,
    GLUT_WINDOW_WIDTH,
    GLUT_WINDOW_HEIGHT,
)
from PIL import Image


class PhotoSphereViewer:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.correction_heading = 0.0
        self.correction_pitch = 0.0
        self.correction_roll = 0.0
        self.heading = 0.0
        self.pitch = 0.0
        self.last_x = None
        self.last_y = None
        self.left_button_down = False
        self.texture_id = None
        self.window_width = 800
        self.window_height = 600
        self.pitch_limit = 90.0  # Degrees
        self.running = True

    def __del__(self):
        if self.texture_id is not None:
            glDeleteTextures(self.texture_id)

    def load_texture(self, path):
        image = Image.open(path)
        xmp = image.getxmp()
        xmp_rdf = xmp.get("xmpmeta", {}).get("RDF", {}).get("Description", [])
        if isinstance(xmp_rdf, dict):
            xmp_rdf = [xmp_rdf]
        for obj in xmp_rdf:
            if "PoseHeadingDegrees" in obj:
                self.correction_heading = float(obj["PoseHeadingDegrees"])
            if "PosePitchDegrees" in obj:
                self.correction_pitch = float(obj["PosePitchDegrees"])
            if "PoseRollDegrees" in obj:
                self.correction_roll = float(obj["PoseRollDegrees"])
        img_data = image.convert("RGB").tobytes()
        width, height = image.size

        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, img_data)

    def draw_sphere(self, radius=50, slices=100, stacks=50):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        quad = gluNewQuadric()
        gluQuadricTexture(quad, GL_TRUE)
        gluQuadricOrientation(quad, GLU_INSIDE)  # View from inside
        gluSphere(quad, radius, slices, stacks)
        gluDeleteQuadric(quad)
        glDisable(GL_TEXTURE_2D)

    @staticmethod
    def draw_horizontal_lines():
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glLineWidth(1.0)

        glBegin(GL_LINES)
        count = 10
        for i in range(count):
            if i == count // 2:
                glColor3f(1, 0, 0)
            else:
                glColor3f(1, 1, 1)
            glVertex2f(0, i * height / count)
            glVertex2f(width, i * height / count)
            glVertex2f(i * width / 10, 0)
            glVertex2f(i * width / 10, height)
        glEnd()

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply yaw and pitch
        glRotatef(self.pitch + 90, 1, 0, 0)  # pitch first
        glRotatef(self.heading, 0, 0, 1)  # then yaw

        glRotatef(self.correction_heading, 0, 0, 1)      # Yaw correction: turn head left/right
        glRotatef(self.correction_roll, 0, -1, 0)     # Roll correction: twist around view axis
        glRotatef(self.correction_pitch, 1, 0, 0)    # Pitch correction: nod head

        self.draw_sphere()
        self.draw_horizontal_lines()

        glutSwapBuffers()

    def reshape(self, width, height):
        self.window_width, self.window_height = width, height
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90.0, width / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def print_rotation(self) -> None:
        print(f"Heading: {self.correction_heading}, Pitch: {self.correction_pitch}, Roll: {self.correction_roll}")

    def keyboard(self, key, x, y):
        if key == b"z":
            self.correction_pitch = max(-90.0, min(90.0, self.correction_pitch + 0.25))
            self.print_rotation()
            glutPostRedisplay()
        elif key == b"c":
            self.correction_pitch = max(-90.0, min(90.0, self.correction_pitch - 0.25))
            self.print_rotation()
            glutPostRedisplay()
        elif key == b"a":
            self.correction_roll = max(-180.0, min(180.0, self.correction_roll + 0.25))
            self.print_rotation()
            glutPostRedisplay()
        elif key == b"d":
            self.correction_roll = max(-180.0, min(180.0, self.correction_roll - 0.25))
            self.print_rotation()
            glutPostRedisplay()
        elif key == b"q":
            self.correction_heading = (self.correction_heading + 1.0) % 360.0
            self.print_rotation()
            glutPostRedisplay()
        elif key == b"e":
            self.correction_heading = (self.correction_heading - 1.0) % 360.0
            self.print_rotation()
            glutPostRedisplay()
        elif key == b"h":
            self.heading = 0.0
            self.pitch = 0.0
            glutPostRedisplay()
        elif key == b"r":
            self.correction_heading = 0.0
            self.correction_pitch = 0.0
            self.correction_roll = 0.0
            self.print_rotation()
            glutPostRedisplay()
        elif key == b"j":
            self.heading = round(self.heading/90) * 90.0 + 90.0
            glutPostRedisplay()
        elif key == b"l":
            self.heading = round(self.heading/90) * 90.0 - 90.0
            glutPostRedisplay()

    def mouse(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            self.left_button_down = (state == GLUT_DOWN)
            self.last_x, self.last_y = x, y

    def motion(self, x, y):
        if self.left_button_down:
            dx = x - self.last_x
            dy = y - self.last_y
            self.last_x, self.last_y = x, y

            sensitivity = 0.2
            self.heading += dx * sensitivity
            # self.pitch -= dy * sensitivity

            # Clamp pitch
            self.pitch = max(-self.pitch_limit, min(self.pitch_limit, self.pitch))

            glutPostRedisplay()

    def init(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def exit(self):
        print("exit")
        subprocess.run([
            EXIF_TOOL_PATH,
            "-overwrite_original",
            f"-XMP-GPano:PoseHeadingDegrees={self.correction_heading}",
            f"-XMP-GPano:PosePitchDegrees={self.correction_pitch}",
            f"-XMP-GPano:PoseRollDegrees={self.correction_roll}",
            self.image_path
        ])
        self.running = False

    def main(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_width, self.window_height)
        glutCreateWindow(b"Photosphere Viewer")

        self.init()
        self.load_texture(self.image_path)

        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshape)
        glutMouseFunc(self.mouse)
        glutKeyboardFunc(self.keyboard)
        glutMotionFunc(self.motion)
        glutWMCloseFunc(self.exit)
        glutMainLoop()


EXIF_TOOL_PATH = r"exiftool.exe"


def main():
    if not os.path.isfile(EXIF_TOOL_PATH):
        raise RuntimeError(EXIF_TOOL_PATH + " does not exist")
    if len(sys.argv) < 2:
        print("Usage: python photosphere_viewer.py (glob:<glob_search_path>)|path>")
        return

    arg = sys.argv[1]
    if arg.startswith("glob:"):
        for path in glob.iglob(sys.argv[1][5:]):
            subprocess.run([
                sys.executable,
                __file__,
                path
            ])
    else:
        viewer = PhotoSphereViewer(arg)
        viewer.main()


if __name__ == "__main__":
    main()
