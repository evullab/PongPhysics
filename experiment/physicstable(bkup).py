# Class for simulating a table for intuitive physics


# Notes: velocities presented in pixels / second

# For walls: 1st is left, 2nd is bottom, 3rd is right, 4th is top

from __future__ import division
from pygame.locals import *
import pygame as pg
import random, math

WHITE = pg.Color('White')
BLACK = pg.Color('Black')
BLUE = pg.Color('Blue')
RED = pg.Color('Red')
GREEN = pg.Color('Green')

# Global direction names
LEFT = 1
RIGHT = 3
BOTTOM = 2
TOP = 4

class PhysicsTable(object):

    def __init__(self, dims, background_cl = WHITE, wall_cl = BLACK, ball_cl = BLUE, ball_rad = , openend = None, badzone = None):
        self.dim = dims
        self.wall_c = wall_cl
        self.bk_c = background_cl
        self.ball_c = ball_cl
        if ball_rad is None:
            self.rad = 0.05 * min(dims)
        else:
            self.rad = ball_rad
        self.bz = badzone
        self.occlude = None

        # Define the surface and start with no walls or balls
        self.surface = pg.Surface(self.dim)
        self.balls = []
        self.walls = []
        self.paddle = None
        self.bounces = 0
        self.sincecol = 0

        # Add an outer wall & catch area (ADD CATCH AREA & LOGIC FOR UNBOUNDING)
        self.addWall((-50,-100),(self.dim[0]+50,2)) # top
        self.addWall((-100,0),(2,self.dim[1])) # left
        self.addWall((-50,self.dim[1]-2),(self.dim[0]+50,self.dim[1]+100)) # bottom
        self.addWall((self.dim[0]-2,0),(self.dim[0]+100,self.dim[1])) # right
        
        
    def addBall(self,initpos,initvel = [0.0,0.0]):
        b = self.Ball(initpos,initvel,self.rad,self.ball_c)
        self.balls.append(b)
        return b

    def addWall(self,upleft,botright, elastic = True):
        w = botright[0] - upleft[0]
        h = botright[1] - upleft[1]
        self.walls.append(self.Wall(pg.Rect(upleft,(w,h)),self.wall_c,elastic))

    def addPaddle(self,initpos,length,h_or_v,fixeddir = True):
        self.paddle = self.Paddle(initpos,length,h_or_v,fixeddir,self.wall_c)

    def draw(self):
        # Clear the surface
        self.surface.fill(self.bk_c)

        # Draw all the walls and balls and basket
        for w in self.walls: w.draw(self.surface)
        for b in self.balls: b.draw(self.surface)
        if self.paddle: self.paddle.draw(self.surface)
        if self.occlude: pg.draw.rect(self.surface, pg.Color('Grey'),self.occlude)

        return self.surface

    def step(self,t = 1/50.0, control = True, mouse = None, stp = 1):
        if mouse:
            self.paddle.move(mouse)
        # Note: should correct this for some overflow fractions at some point...
        for i in range(int(t*1000/stp)):
            r = self.physicsstep(stp)
        return r

    def setOcclude(self, oc = None):
        self.occlude = oc

    # Cleans balls that are off the screen
    def cleanballs(self):
        screenrect = pg.Rect((0,0),self.dim)
        for b in self.balls:
            if not screenrect.colliderect(b.r):
                self.balls.remove(b)

    # Checks whether a ball is caught by the paddle,or in a failure region defined by a Rect (returns True for good catch, False for bad, None otherwise) 
    def checkcatch(self, ball, failrect = None):
        p1 = self.paddle.p
        p2 = self.paddle.getlr()
        if self.intersect_ball_line(ball,(p1,p2)): return True
        elif failrect and failrect.collidepoint((ball.x,ball.y)): return False
        else: return None

    # Stops and recolors balls; returns list of checkcatch for all balls
    def catches(self, failrect = None, good_col = GREEN, bad_col = RED):
        ret = []
        for b in self.balls:
            r = self.checkcatch(b,failrect)
            ret.append(r)
            if r == True:
                b.stop()
                b.col = good_col
            elif r == False:
                b.stop()
                b.col = bad_col
        return ret

    def fails(self,failrect):
        for b in balls:
            if failrect.collidepoint((b.x,b.y)): return True
        return False

    # Physics methods

    def distance(self,p1,p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx*dx + dy*dy)

    # Tests whether a ball intersects a line segment defined between two points in the array ps
    # See equations at: http://paulbourke.net/geometry/sphereline/
    def intersect_ball_line(self,ball,ps):
        x1, y1 = ps[0]
        x2, y2 = ps[1]
        xc, yc = ball.x, ball.y

        a = (x2 - x1)**2 + (y2 - y1)**2
        b = 2*((x2-x1)*(x1-xc)+(y2-y1)*(y1-yc))
        c = xc**2 + yc**2 +x1**2 + y1**2 -2*(xc*x1 + yc*y1) - ball.rad**2

        det = b**2 - 4*a*c
        if det < 0: return False
        s1 = (b*-1 + math.sqrt(det))/(2*a)
        s2 = (b*-1 - math.sqrt(det))/(2*a)
        if (s1 >= 0 and s1 <= 1) or (s2 >= 0 and s2 <= 1): return True
        else: return False
        
    # Test whether there is a ball-wall collision; return the direction the ball hits from or False if no collision
    def collide_ball_wall(self,ball,wall):
        if wall.r.colliderect(ball.r):
            # If it sees a collision, it needs to test which direction (or whether there actually was a collision due to the circularity)
            if self.intersect_ball_line(ball,wall.side(RIGHT)): return LEFT
            elif self.intersect_ball_line(ball,wall.side(LEFT)): return RIGHT
            elif self.intersect_ball_line(ball,wall.side(BOTTOM)): return TOP
            elif self.intersect_ball_line(ball,wall.side(TOP)): return BOTTOM
            else: raise(Exception("Physics error in collide_ball_wall"))
        else:
            return False

    # Test whether there is a ball-ball collision; return the angle of the collision point from the center of the first ball, or False if no collision
    def collide_ball_ball(self,ball1,ball2):
        if distance(ball1.r.center,ball2.r.center) > (ball1.rad + ball2.rad): return False
        dx = ball1.r.centerx - ball2.r.centerx
        dy = ball1.r.centery - ball2.r.centery
        return math.tan(dy / dx)
        
    # Move all of the balls by a certain number of steps (defaults to 1 step/ms, may need to be adjusted for performance issues)
    def physicsstep(self,s = 1):
        self.sincecol += 1
        for b in self.balls:
            # Move the ball
            b.move(s)
            # Test for collisions - currently only one collision per time step allowed
            frcl = True
            for w in self.walls:
                if frcl:
                    c = self.collide_ball_wall(b,w)
                    if c != False:
                        self.sincecol = 0
                        self.bounces += 1
                        frcl = False
                        # Inelastic collision: move back and stop the ball
                        if w.e == False:
                            b.move(-s)
                            b.stop()
                        # Elastic collision: 
                        else:
                            b.bounce(c)
            # Someday will also need to add ball-ball collisions (for any multi-ball experiments)
            # Check for catches
        ret = None
        if self.paddle: ret = self.catches(self.bz)
        return ret
        

    # Ball and wall classes to place on the table

    class Ball(object):
        def __init__(self,initpos,initvel = [0.0,0.0],size = 10,color = BLACK):
            self.rad = int(size)
            self.x = initpos[0]
            self.y = initpos[1]
            self.col = color
            self.v = initvel
            self.r = pg.Rect(0,0,0,0)
            self.r.center = (int(self.x),int(self.y))
            self.r.width, self.r.height = self.rad, self.rad
            self.bounces = 0

        def draw(self,surface):
            x = int(self.r.center[0])
            y = int(self.r.center[1])
            pg.draw.circle(surface,self.col,(int(x),int(y)),int(self.rad))

        def stop(self):
            self.v = (0,0)

        def getpos(self):
            return (self.x,self.y)

        def move(self, s = 1):
            self.x += self.v[0] * s / 1000
            self.y += self.v[1] * s / 1000
            self.r.centerx = int(self.x)
            self.r.centery = int(self.y)

        def bounce(self, direction):
            self.bounces += 1
            if direction == LEFT or direction == RIGHT: self.v = (-self.v[0],self.v[1])
            if direction == TOP or direction == BOTTOM: self.v = (self.v[0],-self.v[1])

        def display(self):
            print self.x, self.y
            print self.rad
            print self.v
            print self.bounces

    class Wall(object):
        def __init__(self,rect, color = BLACK, elastic = True):
            self.r = rect
            self.col = color
            self.e = elastic

        def draw(self,surface):
            pg.draw.rect(surface,self.col,self.r)

        def corners(self):
            return([self.r.topleft,self.r.bottomleft,self.r.topright,self.r.bottomright])

        def side(self,direction):
            if direction == LEFT: return([self.r.topleft, self.r.bottomleft])
            elif direction == RIGHT: return([self.r.topright,self.r.bottomright])
            elif direction == TOP: return([self.r.topleft,self.r.topright])
            elif direction == BOTTOM: return([self.r.bottomleft,self.r.bottomright])
            else: return None


    # Paddle class for catching balls - like a short, inelastic, movable wall
    class Paddle(object):
        def __init__(self,initpos, length, direct = 'h', fixeddir = True, color = BLACK):
            self.p = initpos
            self.fixx, self.fixy = False, False
            if direct == 'h':
                self.l = (length, 0)
                if fixeddir: self.fixy = True
            else:
                self.l = (0, length)
                if fixeddir: self.fixx = True
            self.col = color
            
        def getlr(self):
            return (self.p[0] + self.l[0], self.p[1] + self.l[1])
            

        def draw(self,surface):
            lr = self.getlr()
            pg.draw.line(surface,self.col,self.p,lr,3)

        def move(self,mousepos):
            # Find the upper corner
            newx = mousepos[0] - int(self.l[0] / 2)
            newy = mousepos[1] - int(self.l[1] / 2)

            # Stay if fixed
            if self.fixx: newx = self.p[0]
            if self.fixy: newy = self.p[1]
            self.p = (newx,newy)

        def getcenter(self):
            return (self.p[0] + self.l[0]/2, self.p[1] + self.l[1]/2)


if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((1000,600))
    clock = pg.time.Clock()
    running = True

    table = PhysicsTable((800,400))
    #missgoal = pg.Rect((0,0), (50,400))
    #table.addWall((400,0),(400,500))
    #table.addBasket((50,275),(20,50),'r', fixeddir = True)
    pg.mouse.set_visible(False)
    table.addBall((400,200),(300,100))

    tstep = 40
    ticks = []

    while running:
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

        tscreen = table.draw()
        screen.blit(tscreen,(100,100))
        pg.display.flip()
        if pg.mouse.get_focused():
            table.step(1/tstep,True,pg.mouse.get_pos())
        else:
            table.step(1/tstep,False,None)
        table.cleanballs()
        #table.catches(missgoal)
        clock.tick(tstep)
        ticks.append(clock.get_time())
        pg.display.set_caption("FPS: " + str(clock.get_fps()))

    print ticks
