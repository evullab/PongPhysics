# Makes stimuli for intuitive physics expt

from __future__ import division
from physicstable import PhysicsTable
import math, random, time
import pygame as pg
from pygame.locals import *

# Constants from the actual experiment - change with input file
from intuitivephys import leadsteps, frrate, v, ballsize

xend = 50 + ballsize

def trback(endpos, d, theta, dims,exd = 0,fail = None, timestep = 1000, drawscreen = None):
    tnew = PhysicsTable(dims)
    v = (d+exd)/timestep * 1000
    tbch = int(1000*d/v)
    #print tbch, d, v
    vx = v * math.cos(theta)
    vy = v * math.sin(theta)
    b = tnew.addBall(endpos,(vx,vy))
    for i in range(timestep):
        tnew.physicsstep()
        if i == tbch: bn = b.bounces
        if fail and tnew.fails(fail): return None,None,None,None
        if drawscreen and (i % 20) == 0:
            drawscreen.blit(tnew.draw(),(0,0))
            pg.display.flip()
    pos = (b.x,b.y)
    # NOTE: Need to fix periodicity of pi here...
    tht = (math.atan(b.v[1]/b.v[0]) + math.pi)
    if b.v[0] < 0: tht += math.pi
    tht = tht % (2*math.pi)
    #bn = b.bounces
    runupsteps = tnew.sincecol
    runupd = v * runupsteps
    if drawscreen: time.sleep(2)
    return pos,tht,bn,runupd

ofl = open('IntuitivePhysExamples.csv','w')
ofl.write('TrialNo,TableDim,Distance,Bounces,Start_x,Start_y,V_theta,End_x,End_y,Sim_theta\n')

# Set the first three in stone - straight line, angled line, one bounce
ofl.write('0,1000x900,0,0,910,450,3.1415926535897931,60,450,0\n')
ofl.write('0,1000x900,0,0,860,200,2.5829933382462307,60,700,0\n')
ofl.write('0,1000x900,0,0,860,700,4.1932428661381671,60,700,0\n')

tdims = [(1200,800),(700,500),(1000,900)]
tdimwrt = ['1200x800','700x500','1000x900']
ds = [800,1200]
extrad = 400
# Written as dimension index, distance index, num bounces
triallist = [(1,0,1),(0,1,1),(2,1,1),(0,0,1),(0,1,1),(1,0,1),(1,1,2),(2,0,1),(2,1,1)]

ntrials = [1,1,1,1,1,1,1,1,1]

tn = 0

# Now iterate through all trial types and find potential starting positions
for t, n in zip(triallist,ntrials):
    for i in range(n):
        tn += 1
        dm = tdims[t[0]]
        dmwrt = tdimwrt[t[0]]
        dist = ds[t[1]]
        bounce = t[2]
        failer = pg.Rect((0,0),(49,dm[1]))
        needsfinding = True

        while needsfinding:
            # Randomly initialize where to end up
            epos = (xend,random.randint(int(dm[1]*.2),int(dm[1]*.8)))
            thend = ((random.random()-0.5) * 0.9 * math.pi) % (2*math.pi)

            spos, etht, bn, runup = trback(epos,dist,thend,dm, extrad,failer)

            # Test whether it fits the number of bounces & run up distance
            if spos is not None and bn == bounce and runup > 200:
                # Then make sure it simulates out correctly
                fwdtbl = PhysicsTable(dm, badzone = pg.Rect((0,0),(xend,dm[1])))
                bvel = (v*math.cos(etht),v*math.sin(etht))
                fwdtbl.addBall(spos,bvel)
                running = True
                its = 0
                prebounce = 0
                while running:
                    fwdtbl.step(1/frrate,False)
                    its += 1
                    if its == leadsteps:
                        prebounce = fwdtbl.ball.bounces
                    pball = fwdtbl.ball.getpos()
                    if pball[0] <= epos[0]:
                        running = False
                        dx = pball[0]-epos[0]
                        dy = pball[1]-epos[1]
                        mvdst = math.sqrt(dx*dx + dy*dy)
                        if mvdst <=1 and fwdtbl.ball.bounces == (bn+prebounce): needsfinding = False

    
        oline = str(tn)+','+dmwrt + ','+str(dist)+','+str(bounce)+','+str(spos[0])+','+str(spos[1])+','+str(etht)+','+str(epos[0])+','+str(epos[1])+','+str(thend)+'\n'
        print oline
        ofl.write(oline)

ofl.close()
