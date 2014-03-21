# Makes stimuli for intuitive physics expt

from __future__ import division
from physicstable import PhysicsTable
import math, random, time
import pygame as pg
from pygame.locals import *

# Constants from the actual experiment - change with input file
from intuitivephys import frrate, ballsize

#xend = 50 + ballsize
muob = 200 # Minimum distance since 

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
            tnew.sincecol = 0
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
    #print exd, runupsteps, (v*runupsteps/1000)
    runupd = exd - (v * runupsteps)/1000
    if drawscreen: time.sleep(2)
    return pos,tht,bn,runupd, occpos, occtht, postb

ofl = open('IntuitivePhysTrials.csv','w')
ofl.write('TrialNo,TableDim,Distance,Bounces,Velocity,RunUpD,Start_x,Start_y,V_theta,Occl_x,Occl_y,Occl_theta,End_x,End_y,Sim_theta,Prebounces\n')

tdims = [(1200,900)]
tdimwrt = ['1200x900']
ds = [600,800,1000]
vs = [600]
extrads = [400]
# Written as dimension index, distance index, num bounces
triallist = [(0,0,0,0,0),(0,0,1,0,0),(0,0,2,0,0),(0,1,0,0,0),(0,1,1,0,0),(0,1,2,0,0),(0,2,0,0,0),(0,2,1,0,0),(0,2,2,0,0)]

ntrials = [72,72,72,72,72,72,72,72,72]

tn = 0

# Now iterate through all trial types and find potential starting positions
for t, n in zip(triallist,ntrials):
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

            #print runup
            #if runup == 1.0: print spos, bn, bounce,bn==bounce,'\n'

            # Skip if there is more than one bounce prior to occlusion (comment out to allow)
            if pstb > 1: continue

            # Test whether it fits the number of bounces & run up distance
            if spos is not None and bn == bounce:
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
                        if mvdst >1 and fwdtbl.ball.bounces != pstb: running  = False
                        sincebounce = fwdtbl.sincecol * v / 1000
                        if sincebounce < muob: running = False
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
