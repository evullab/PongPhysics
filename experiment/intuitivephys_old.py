# Intuitive Physics

# NOTE: NEED TO ADD A CHECK TO ENSURE THAT THE BALL ACTUALLY GOES THROUGH THE TARGET!!!

from __future__ import division
from physicstable import PhysicsTable
import math, random, time
import pygame as pg
from pygame.locals import *

# Trace back to where a ball should be placed to hit the endpoint; returns startpos, starttheta, and numbounce
# Note: Theta is the angle to move BACKWARDS
def traceback_old(endpos, d, theta, dims):
    xst = endpos[0]
    yst = endpos[1]
    xmax = dims[0]
    ymax = dims[1]

    theta = theta % (2*math.pi)

    xmv = d * math.cos(theta)
    ymv = d * math.sin(theta)

    # Find the starting position
    xb = math.floor((xst + xmv) / xmax)
    
    # Flip for negative movement
    if xb < 0: xstp, xmvp = (xmax - xst), -xmv
    else: xstp, xmvp = xst, xmv
    
    if xb % 2 == 0: xend = (xstp + xmvp) - (abs(xb) * xmax)
    else: xend = xmax - ((xstp + xmvp) - (abs(xb) * xmax))
    if xb < 0: xend = xmax - xend

    yb = math.floor((yst + ymv) / ymax)
    # Flip for negative movement
    if yb < 0: ystp, ymvp = (ymax - yst), -ymv
    else: ystp, ymvp = yst, ymv
    
    if yb % 2 == 0: yend = (ystp + ymvp) - (abs(yb) * ymax)
    else: yend = ymax - ((ystp + ymvp) - (abs(yb) * ymax))
    if yb < 0: yend = ymax - yend

    thetast = (theta + math.pi) % (2*math.pi)
    # Flip horizontally if odd bounces
    if xb % 2 == 1: thetast = (math.pi-thetast) %(2*math.pi)
    # Flip vertically if odd bounces
    if yb % 2 == 1: thetast = (2*math.pi - thetast)

    nbounce = abs(xb) + abs(yb)

    return (xend,yend),thetast,nbounce

def trback(endpos, d, theta, dims, timestep = 1000, drawscreen = None):
    tnew = PhysicsTable(dims)
    v = d/timestep * 1000
    vx = v * math.cos(theta)
    vy = v * math.sin(theta)
    b = tnew.addBall(endpos,(vx,vy))
    for i in range(timestep):
        tnew.physicsstep()
        if drawscreen and (timestep % 50) == 0:
            drawscreen.blit(tnew.draw(),(0,0))
            pg.display.flip()
    pos = (b.x,b.y)
    tht = (math.atan(b.v[1]/b.v[0]) + math.pi) % (2*math.pi)
    bn = b.bounces
    if drawscreen: time.sleep(2)
    return pos,tht,bn

if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((800,600))
    clock = pg.time.Clock()
    running = True

    stpt = (50,150)
    tabledim = (800,400)
    frrate = 50

    table = PhysicsTable(tabledim)
    #table.addBasket(stpt,(40,100),'r')
    #pg.mouse.set_visible(False)

    d = 800
    v = 50
    #ts = [.25*math.pi,1.75*math.pi]
    #tdim = (tabledim[0] - table.rad, tabledim[1] - table.rad)
    for i in range(1):
        thend = ((random.random()-0.5) * math.pi) % (2*math.pi)
        #print thend
        #thend = ts[i]
        bpt, theta, n = trback((90,200),d,thend,tabledim,drawscreen = None)
        print theta
        vx = v * math.cos(theta)
        vy = v * math.sin(theta)
        print bpt, vx, vy
        #print ''
        table.addBall(bpt,(vx,vy))

    stt = time.time()
    its = 0
    times = []
    while running:
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
        tscreen = table.draw()
        pg.draw.circle(tscreen,pg.Color('Green'),(90,200),10)
        screen.blit(tscreen,(0,100))
        pg.display.flip()
        if pg.mouse.get_focused():
            table.step(1/frrate,True,pg.mouse.get_pos())
        else:
            table.step(1/frrate,False,None)
        table.cleanballs()
        '''
        ca = table.catches(None)
        try:
            if (len(ca) != 0) & (ca[0] == True):
                print (time.time() - stt), its
                table.balls[0].remove(table.phys)
                table.balls.remove(table.balls[0])
        except:
            print (time.time() - stt), its
            running = False
        clock.tick(frrate)
        times.append(clock.get_time())
        its += 1
        '''

    print times
    
