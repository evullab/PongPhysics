# pyText
#
# Helper methods for centering and writing text onto a screen

from __future__ import division
import pygame as pg
import time
from pygame.locals import *

pg.init()

# Constants
FONT_L = pg.font.SysFont(None,48)
FONT_M = pg.font.SysFont(None,36)
FONT_S = pg.font.SysFont(None,24)
FONT_VL = pg.font.SysFont(None,72)

LEFT = 1
RIGHT = 3
BOTTOM = 2
TOP = 4
CENTER = 5

# Parse list of text into lines not exceeding a given width based for a given rendering
# Returns a list of strings comprising the different lines
def parse_text(text,width,font = None, parser = ' '):
    if font == None:
        font = FONT_L
    textList = text.split(parser)
    ret = []
        
    # Iterate cutting lines until all text has been split
    while len(textList) != 0:
        # Ensure that at least one word fits within the line
        if font.size(textList[0])[0] > width:
            print("Error: Font size too large to render")
            return []
         
        # Determine the longest list that will fit within the width
        for j in range(1,len(textList)+1):
            # Split if newline character is found
            if textList[j-1] == '\n':
                if j == 1:
                    ret.append("")
                    textList = textList[j:]
                else:
                    ret.append(" ".join(textList[0:j-1]))
                    textList = textList[j:]
                break
                    
            line = " ".join(textList[0:j])
            junk = font.size(line)
            if font.size(line)[0] > width:
                ret.append(" ".join(textList[0:j-1]))
                textList = textList[j-1:]
                break
            # Send last line in as well
            if j == len(textList):
                ret.append(line)
                textList = []
                break
    return ret

# Renders text with a given justification
def justify_text(text,font,pos,horizontal = CENTER, vertical = CENTER,color = pg.Color('Black')):
    # Check for text inputs
    if horizontal == 'right': horizontal = RIGHT
    elif horizontal == 'left': horizontal = LEFT
    elif horizontal == 'center': horizontal = CENTER
    elif horizontal not in [RIGHT,LEFT,CENTER]: raise Exception('Not valid horizontal justification: ' + str(horizontal))

    if vertical == 'top': vertical = TOP
    elif vertical == 'bottom': vertical = BOTTOM
    elif vertical == 'center': vertical = CENTER
    elif vertical not in [TOP,BOTTOM,CENTER]: raise Exception('Not valid vertical justification: ' + str(vertical))

    tobj = font.render(text,True,color)
    trect = tobj.get_rect()
    x = pos[0]
    y = pos[1]

    if horizontal == RIGHT: trect.right = x
    if horizontal == LEFT: trect.left = x
    if horizontal == CENTER: trect.centerx = x

    if vertical == TOP: trect.top = y
    if vertical == BOTTOM: trect.bottom = y
    if vertical == CENTER: trect.centery = y

    return tobj,trect

def quitevent(quit_k = [K_LSHIFT,K_ESCAPE]):
    keys = pg.key.get_pressed()
    for k in quit_k:
        if keys[k] == 0:
            return False
    return True

# Displays instruction text then waits for a keypress or mouse-click to move on (moving on can be disabled for each)
# Returns True if a quit action is given, False if a move-on action is given
def display_instructions(text,screen,keymove = True,clickmove = True,font = FONT_VL,txtcol = pg.Color('Black'),bkcol = pg.Color('White')):
    sdim = screen.get_size()
    xwid = int(0.9 * sdim[0])
    ymid = int(sdim[1]/2)
    xmid = int(sdim[0]/2)
    
    phrases = parse_text(text,xwid,font)
    vheight = font.get_linesize()
    txtheight = vheight * len(phrases)

    yst = int(ymid - txtheight/2 + vheight/2)

    # Draw the text
    screen.fill(bkcol)
    for i in range(len(phrases)):
        ypos = yst + i*vheight
        t, tr = justify_text(phrases[i],font,(xmid,ypos),CENTER,TOP,txtcol)
        screen.blit(t,tr)
    pg.display.flip()

    # Wait a second to ensure people don't just click through
    time.sleep(1)

    # Wait for a move on signal
    while True:
        for e in pg.event.get():
            if e.type == QUIT: return True
            elif e.type == KEYDOWN:
                if keymove and (e.key != K_ESCAPE and e.key != K_LSHIFT): return False
                if quitevent(): return True
            elif e.type == MOUSEBUTTONDOWN and clickmove: return False
