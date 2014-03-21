# Makes stimuli for intuitive physics expt

from __future__ import division
from physicstable import PhysicsTable
import math, random, time
import pygame as pg
from pygame.locals import *

# Constants from the actual experiment - change with input file
from intuitivephys import frrate, ballsize

#xend = 50 + ballsize

def trback(endpos, d, theta, dims,exd = 0,fail = None, timestep = 1000, drawscreen = None):
    tnew = PhysicsTable(dims, active = True)
    v = (d+exd)/timestep * 1000
    tbch = int(1000*d/v)
    #print tbch, d, v
    vx = v * math.cos(theta)
    vy = v * math.sin(theta)
    b = tnew.addBall(endpos,(vx,vy))
    for i in range(timestep):
        tnew.physicsstep()
        if i == tbch:
            bn = b.bounces
            tnew.deactivate()
            occpos = (b.x,b.y)
            occv = b.v
        if fail and tnew.fails(fail): return None,None,None,None
        if drawscreen and (i % 20) == 0:
            drawscreen.blit(tnew.draw(),(0,0))
            pg.display.flip()
    pos = (b.x,b.y)
    # Find angle of velocity
    tht = (math.atan(b.v[1]/b.v[0]) + math.pi)
    if b.v[0] < 0: tht += math.pi
    tht = tht % (2*math.pi)
    # And for the velocity at occlusion
    occtht = (math.atan(occv[1]/occv[0]) + math.pi)
    if occv[0] < 0: occtht += math.pi
    occtht = occtht % (2*math.pi)

    # Find the number of bounces prior to occlusion
    postb = b.bounces - bn
    
    runupsteps = tnew.sincecol
    runupd = v * runupsteps
    if drawscreen: time.sleep(2)
    return pos,tht,bn,runupd, occpos, occtht, postb

ofl = open('IntuitivePhysExamples.csv','w')
ofl.write('TrialNo,TableDim,Distance,Bounces,Velocity,RunUpD,Start_x,Start_y,V_theta,Occl_x,Occl_y,Occl_theta,End_x,End_y,Sim_theta,Prebounces\n')

# Write the simple example trials
ofl.write('1,1200x900,0,0,600,400,1150,450,'+str(math.pi)+',0,0,0,620,450,0,0\n')
ofl.write('2,1200x900,0,0,600,400,1120,150,'+str(math.atan(-6.0/5.0)+math.pi)+',0,0,0,620,750,0,0\n')
ofl.write('3,1200x900,0,1,600,400,1020,450,'+str(math.atan(4.5/2.0)+math.pi)+',0,0,0,620,450,0,0\n')
ofl.write('4,1200x900,0,0,600,400,1150,150,'+str(math.atan(-6.0/2.5)+math.pi)+',0,0,0,900,750,0,0\n')
ofl.write('5,1200x900,0,0,600,400,850,450,'+str(math.pi)+',0,0,0,150,450,0,0\n')

tdims = [(1200,900)]
tdimwrt = ['1200x900']
ds = [500,800]
vs = [600]
extrads = [400]
# Written as dimension index, distance index, num bounces, velocity, runup d
triallist = [(0,0,0,0,0),(0,1,0,0,0),(0,0,2,0,0),(0,1,1,0,0),(0,0,0,0,0),(0,1,2,0,0),(0,0,1,0,0)]

ntrials = [1,1,1,1,1,1,1]

tn = 5

# Now iterate through all trial types and find potential starting positions
for t, n in zip(triallist,ntrials):

    if tn==6:
        ofl.write('7,1200x900,0,0,600,400,600,450,0.0,0,0,0,800,450,0,0\n')
        tn += 1
    
    for i in range(n):
        tn += 1
        dm = tdims[t[0]]
        dmwrt = tdimwrt[t[0]]
        dist = ds[t[1]]
        bounce = t[2]
        v = vs[t[3]]
        extrad = extrads[t[4]]
        failer = pg.Rect((0,0),(49,dm[1]))
        needsfinding = True

        while needsfinding:
            # Randomly initialize where to end up
            # xposition - anywhere except the first 50 or last 200 pixels + ball size (or le
            # yposition - in the middle 60% of the screen
            if bounce == 0: maxx = dm[0]-dist
            else: maxx = dm[0]-150
            if bounce == 2 and dist == 600: minx = dm[0]-400
            else: minx = 50
            x_epos = random.randint(minx,maxx)+ballsize
            y_epos = random.randint(int(dm[1]*.2),int(dm[1]*.8))
            epos = (x_epos,y_epos)
            thend = ((random.random()-0.5) * 0.85 * math.pi) % (2*math.pi)

            spos, etht, bn, runup, opos, otht, pstb = trback(epos,dist,thend,dm,extrad,failer)

            # Skip if there is more than one bounce prior to occlusion (comment out to allow)
            if pstb > 1: continue

            # Test whether it fits the number of bounces & run up distance
            if spos is not None and bn == bounce and runup > 200:
                # Then make sure it simulates out correctly
                totsteps = math.ceil((extrad + dist)/v * frrate)
                fwdtbl = PhysicsTable(dm, badzone = pg.Rect((0,0),(x_epos,dm[1])), active = False)
                bvel = (v*math.cos(etht),v*math.sin(etht))
                fwdtbl.addBall(spos,bvel)
                running = True
                its = 0
                prebounce = 0
                leadsteps = math.ceil(extrad/v * frrate)
                while running:
                    fwdtbl.step(1/frrate,False)
                    its += 1
                    pball = fwdtbl.ball.getpos()
                    if its == leadsteps:
                        prebounce = fwdtbl.ball.bounces
                        fwdtbl.activate()
                        dx = pball[0]-opos[0]
                        dy = pball[1]-opos[1]
                        mvdst = math.sqrt(dx*dx + dy*dy)
                        if mvdst >1 and fwdtbl.ball.bounces != pstb: continue
                    if its == totsteps: #NEED TO FIND A DIFFERENT TEST FOR THIS!!!!! USE NUMBER OF ITERATIONS!!!!
                        running = False
                        dx = pball[0]-epos[0]
                        dy = pball[1]-epos[1]
                        mvdst = math.sqrt(dx*dx + dy*dy)
                        if mvdst <=1 and fwdtbl.ball.bounces == (bn+prebounce): needsfinding = False

        oline = str(tn)+','+dmwrt + ','+str(dist)+','+str(bounce)+','+str(v)+','+str(extrad)+','+str(spos[0])+','+str(spos[1])+','+str(etht)+','
        oline += str(opos[0])+','+str(opos[1])+','+str(otht)+','+str(epos[0])+','+str(epos[1])+','+str(thend)+','+str(prebounce)+'\n'
        print oline
        ofl.write(oline)

ofl.close()
