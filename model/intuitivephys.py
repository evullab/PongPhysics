# Intuitive Physics

from __future__ import division
from physicstable_dynam import PhysicsTable
import math, random, time, sys, os
import pygame as pg
from pygame.locals import *
from pyText import *
from parseFiles import inputConfig
import ipinstruct

# Import constants (also used in program to create stimuli)
opts = inputConfig(os.path.join(os.getcwd(),'Input','IntPhysOptions.txt'))

frrate = opts['FrameRate']
paddlelen = opts['PaddleLen']
ballsize = opts['BallRad']
if opts['Fullscreen'] == True: fullsc = pg.FULLSCREEN
else: fullsc = 0

trialfl = os.path.join(os.getcwd(),'Input','IntuitivePhysTrials.csv')
samptrialfl = os.path.join(os.getcwd(),'Input','IntuitivePhysExamples.csv')
outputflbase = os.path.join(os.getcwd(),'Output','IntPhysOut_')
consolidatedfl = os.path.join(os.getcwd(),'Output','SummaryOutput.txt')


class Trial(object):
    def __init__(self,flln):
        l = flln.strip().split(',')
        self.n = int(l[0])
        dimstr = l[1].split('x')
        self.dim = (int(dimstr[0]),int(dimstr[1]))
        self.dist = int(l[2])
        self.v = int(l[4])
        self.runup = int(l[5])
        self.bounces = int(l[3])
        self.initpos = (float(l[6]),float(l[7]))
        tht = float(l[8])
        self.vel = (self.v*math.cos(tht),self.v*math.sin(tht))
        self.occpos = (float(l[9]),float(l[10]))
        self.occtht = float(l[11])
        self.endpt = (int(l[12]),int(l[13]))
        self.prebounce = int(l[15])
        self.dimtxt = l[1]
        self.leadsteps = math.ceil(self.runup/self.v * frrate)

    def hitEnd(self,pt):
        if abs(pt[0]-self.endpt[0]) <= 2 and abs(pt[1]-self.endpt[1]) <= 2: return True
        elif pt[0] <= 50: return False
        else: return None

    def pr(self):
        print self.dim, self.dist, self.bounces, self.initpos, self.vel, self.endpt

def prtexttop(text,screen,yoff, xleft, xright,score):
    ybottom = yoff-20
    if text is not None:
        t,tr = justify_text(text,FONT_L,(xleft,ybottom),LEFT,BOTTOM)
        screen.blit(t,tr)
    if score is not None:
        t,tr = justify_text('Score: ' + str(score),FONT_L,(xright,ybottom),RIGHT,BOTTOM)
        screen.blit(t,tr)

def safequit(cfl = None):
    if cfl: cfl.close()
    pg.quit()
    sys.exit(0)

def runtrial(trial, screen,score, sID,outfile = None,nt = 0, noocclude = False):
    if opts['PrintTrial'] == True: trial.pr()
    its = 0
    leads = trial.leadsteps
    prebounce = 0
    running = True
    catch = None
    failarea = pg.Rect((0,0),(trial.endpt[0]-15,trial.dim[1]))
    paddley = None
    toffset = (int((screen.get_size()[0]-trial.dim[0])/2),100 + int((screen.get_size()[1]-trial.dim[1]-100)/2))
    table = PhysicsTable(trial.dim, ball_rad = ballsize, badzone = failarea, active = False)
    
    table.addPaddle((trial.endpt[0]-ballsize,trial.dim[1]/2),paddlelen,'v',True)
    #targx = 50 + ballsize

    clock = pg.time.Clock()

    # Let the subject get set up
    running = True
    while running:
        for event in pg.event.get():
            if event.type == QUIT: safequit(outfile)
            elif event.type == KEYDOWN and quitevent(): safequit(outfile)
            elif event.type == MOUSEBUTTONDOWN: running = False
            
        if pg.mouse.get_focused():
            mp = pg.mouse.get_pos()
            mpoff = (mp[0] - toffset[0], mp[1] - toffset[1])
            r = table.step(1/frrate,True,mpoff,xtarg = trial.endpt[0])
        else:
            r = table.step(1/frrate,False,None,xtarg = trial.endpt[0])

        clock.tick(frrate)
        pg.display.set_caption('FPS: ' + str(clock.get_fps()))

        screen.fill(pg.Color('White'))
        prtexttop("Click to shoot the ball",screen,toffset[1],toffset[0],toffset[0]+trial.dim[0],score)
        tscreen = table.draw()
        screen.blit(tscreen,toffset)
        pg.display.flip()

    # Add the ball and start the trial
    table.addBall(trial.initpos,trial.vel)

    running = True
    table.sincecol = 0
    while running:
        for event in pg.event.get():
            if event.type == QUIT: safequit(outfile)
            elif event.type == KEYDOWN and quitevent(): safequit(outfile)

        if pg.mouse.get_focused():
            mp = pg.mouse.get_pos()
            mpoff = (mp[0] - toffset[0], mp[1] - toffset[1])
            r = table.step(1/frrate,True,mpoff,xtarg = trial.endpt[0])
        else:
            r = table.step(1/frrate,False,None,xtarg = trial.endpt[0])
        its += 1
        if its == leads:
            prebounce = table.ball.bounces
            table.activate()

        clock.tick(frrate)
        pg.display.set_caption('FPS: ' + str(clock.get_fps()))

        screen.fill(pg.Color('White'))
        prtexttop(None,screen,toffset[1],toffset[0],toffset[0]+trial.dim[0],score)
        tscreen = table.draw()
        if its > leads and noocclude == False: pg.draw.rect(tscreen,pg.Color('Grey'),Rect((trial.endpt[0]-ballsize+3,1),(trial.dim[0]-trial.endpt[0]+ballsize-4,trial.dim[1]-2)))
        screen.blit(tscreen,toffset)
        pg.display.flip()

        catch = table.catches()
        if catch == True or catch == False:
            running = False
            paddley = table.padend
            if paddley is None:
                print table.paddle.getcenter()[1]
                print table.ball.getpos()
                raise Exception('DID NOT CAPTURE PADDLE LOCATION')

    # Show results of trial
    if catch == True:
        fintxt = 'Nice catch! Click for the next trial'
        if score is not None: score += 1
    else: fintxt = 'You missed. Click for the next trial'
    running = True
    while running:
        for event in pg.event.get():
            if event.type == QUIT: safequit(outfile)
            elif event.type == KEYDOWN and quitevent(): safequit(outfile)
            elif event.type == MOUSEBUTTONDOWN: running = False

        clock.tick(frrate)
        pg.display.set_caption('FPS: ' + str(clock.get_fps()))

        screen.fill(pg.Color('White'))
        prtexttop(fintxt,screen,toffset[1],toffset[0],toffset[0]+trial.dim[0],score)
        tscreen = table.draw()
        screen.blit(tscreen,toffset)
        pg.display.flip()

    pixeldiff = (paddley - trial.endpt[1])
    pixelsoff = abs(pixeldiff)

    # Write to output file
    if outfile:
        outfile.write(sID+','+str(nt)+','+str(trial.n)+','+trial.dimtxt+','+str(trial.dist)+','+str(trial.bounces)+','+str(trial.v)+','+str(trial.runup)+',')
        outfile.write(str(catch)+','+str(trial.endpt[0])+','+str(trial.endpt[1])+','+str(paddley)+','+str(pixeldiff)+','+str(pixelsoff)+','+str(prebounce)+'\n')
    
    return catch, pixelsoff

def runinstructs(samples,screen):
    # Welcome and let people just move the paddle around
    if display_instructions(ipinstruct.welcome,screen,keymove = False): safequit()
    table = PhysicsTable((1000,900))
    table.addPaddle((50,450),paddlelen,'v',True)
    toffset = (int((screen.get_size()[0]-1000)/2),100 + int((screen.get_size()[1]-900-100)/2))
    running = True
    while running:
        for event in pg.event.get():
            if event.type == QUIT: safequit(outfile)
            elif event.type == KEYDOWN and quitevent(): safequit(outfile)
            elif event.type == MOUSEBUTTONDOWN: running = False
            
        if pg.mouse.get_focused():
            mp = pg.mouse.get_pos()
            mpoff = (mp[0] - toffset[0], mp[1] - toffset[1])
            r = table.step(1/frrate,True,mpoff)
        else:
            r = table.step(1/frrate,False,None)

        screen.fill(pg.Color('White'))
        prtexttop("Click to continue",screen,toffset[1],toffset[0],toffset[0]+1000,None)
        tscreen = table.draw()
        screen.blit(tscreen,toffset)
        pg.display.flip()

    # Give instructions and show examples building in complexity
    if display_instructions(ipinstruct.basictrial,screen,keymove=False): safequit()
    runtrial(samples[0],screen,None,None,noocclude = True)
    
    if display_instructions(ipinstruct.slanttrial,screen,keymove=False): safequit()
    runtrial(samples[1],screen,None,None,noocclude = True)
    
    if display_instructions(ipinstruct.bouncetrial,screen,keymove=False): safequit()
    runtrial(samples[2],screen,None,None,noocclude = True)
    
    if display_instructions(ipinstruct.smalltrial,screen,keymove=False): safequit()
    runtrial(samples[3],screen,None,None,noocclude = True)
    
    if display_instructions(ipinstruct.largetrial,screen,keymove=False): safequit()
    runtrial(samples[4],screen,None,None,noocclude = True)
    
    if display_instructions(ipinstruct.occludetrial,screen,keymove=False): safequit()
    runtrial(samples[5],screen,None,None)

    if display_instructions(ipinstruct.greypaddle,screen,keymove=False): safequit()
    runtrial(samples[6],screen,None,None)
    
    if display_instructions(ipinstruct.preexamples,screen,keymove=False): safequit()
    for i in range(7,13):
        runtrial(samples[i],screen,None,None)

    if display_instructions(ipinstruct.postinstruct,screen,keymove=False): safequit()

if __name__ == '__main__':

    sID = raw_input("Please enter subject ID: ")
    outputfl = outputflbase + sID + '.csv'

    # Initialize pygame
    fulldims = (1280,1024)
    pg.init()
    screen = pg.display.set_mode(fulldims,fullsc)

    stime = time.time()

    # Load sample trials
    samptrials = []
    tfls = open(samptrialfl,'rU')
    tfls.next()
    for l in tfls: samptrials.append(Trial(l))

    tfls.close()
    runinstructs(samptrials,screen)

    instdone = int(time.time() - stime)
    
    # Create a table of trials & shuffle them
    trin = []
    tfl = open(trialfl,'rU')
    tfl.next()
    for l in tfl: trin.append(Trial(l))
    trials = random.sample(trin,len(trin))
    tfl.close()
    
    ofl = open(outputfl,'w')
    ofl.write('SubjID,Order,TrialNo,Dim,Dist,Bounces,Velocity,RunUp,Caught,TargetXPos,TargetYPos,PaddleYPos,Diff,AbsDiff,Prebounce\n')
    
    score = 0

    ntri = 0

    pxoff = []
    

    # Test each trial
    for t in trials:
        ntri += 1
        res, poff = runtrial(t,screen,score,sID,ofl,ntri)
        if res == True: score += 1
        pxoff.append(poff)
        # Allow for breaks every quarter (note: only works if # trials is divisible by 4)
        proprtn = (ntri / len(trials)) * 4.0
        brstr = None
        if proprtn == 1.0: brstr = ipinstruct.breakstring.format('a quarter of the way',str(score))
        if proprtn == 2.0: brstr = ipinstruct.breakstring.format('halfway',str(score))
        if proprtn == 3.0: brstr = ipinstruct.breakstring.format('three quarters of the way',str(score))
        if brstr:
            if display_instructions(brstr,screen,keymove=False): safequit(ofl)

    acc = score / len(trials)
    trdone = int(time.time() - instdone - stime)
    display_instructions(ipinstruct.ending.format(str(score),str(int(round(acc*100,0)))),screen)

    # Write out summary stats
    meanoff = sum(pxoff) / len(pxoff)
    avgtime = trdone/len(trials)
    
    consfl = open(consolidatedfl,'a')
    consfl.write('SubjID: ' + sID + '\n')
    consfl.write('Score: ' + str(score) + '\n')
    consfl.write('Accuracy: ' + str(acc) + '\n')
    consfl.write('Mean error: ' + str(meanoff) + '\n')
    consfl.write('Time to complete instructions: ' + str(instdone) + '\n')
    consfl.write('Time to complete all trials: ' + str(trdone) + '\n')
    consfl.write('Avg time per trial: ' + str(avgtime) + '\n\n')
    consfl.close()

    # Cleanup
    safequit(ofl)
