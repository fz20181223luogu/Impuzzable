'''
The main game Impuzzable
Includes GUI and game mechanic for the game.
'''
from __future__ import annotations
import pygame
import json
from Puzzle import UP,RIGHT,DOWN,LEFT
import Puzzle
from copy import deepcopy

window_w,window_h=1280,720
EXIT=-1 # exit code for window function to return if user clicked X to close window

# customize tile and board class so they can have GUI properties
class Tile(Puzzle.Tile): # Tile with GUI
    def __init__(self, x: int, y: int, id: int = -1, adj: list = [0,0,0,0], colour: str = "red"):
        self.x=x
        self.y=y
        self.id=id # Default to be -1 (empty)
        self.adj=adj[:]
        self.colour=colour
    
    def __repr__(self):
        '''visualize tile
        '''
        return ("+--------+\n"+
               f"|   %02d   | (%d %d)\n" % (self.adj[UP],self.x,self.y)+
               f"|%02d %02d %02d|\n" % (self.adj[LEFT],self.id,self.adj[RIGHT])+
               f"|   %02d   |\n" % self.adj[DOWN]+
                "+--------+")
    def rotate(self):
        '''Rotate current tile 90 degrees anticlockwise
        '''
        return Tile(self.x,self.y,self.id,[self.adj[(i+1)%4] for i in range(4)],self.colour)
    def draw(self, len: int, screen: pygame.Surface|None=None, colour: str="", stroke: int=0):
        ''' 
        Draw the tile on given screen and return a sequence of points for pygame to draw the tile on the board
        len be the side length of the tile on canvas (not counting concaved part)
        '''
        def linepts(base_x: int,base_y: int,next_x: int,next_y: int, dir: int, shape: dict)->list:
            '''
            Return a sequence of points for a side of the tile
            ''' 
            lerp=lambda a,b,t: a+t*(b-a) # a progress t (0<=t<=1) between a->b
            ret=[]
            # ret=[(base_x,base_y)]
            for coord in shape["coord"]:
                cx=lerp(base_x,next_x,coord[0]/shape["sep"])
                cy=lerp(base_y,next_y,coord[0]/shape["sep"])
                if base_y==next_y:
                    cy+=(base_x-next_x)*dir*coord[1]/shape["sep"]
                elif base_x==next_x:
                    cx-=(base_y-next_y)*dir*coord[1]/shape["sep"]
                ret.append((round(cx,2),round(cy,2)))
            return ret
        
        with open('pattern.json', 'r') as file:
            shape_lib = json.load(file)
        ret=[]

        # Draw the top pattern
        x,y=self.x-len//2,self.y-len//2 # LU
        ret.append((x,y))
        
        shape=shape_lib[abs(self.adj[UP])-1]
        dir=self.adj[UP]//abs(self.adj[UP])
        ret.extend(linepts(x,y,x+len,y,dir,shape))
        
        # Draw the right pattern
        x,y=self.x+len//2,self.y-len//2 # RU
        ret.append((x,y))
        
        shape=shape_lib[abs(self.adj[RIGHT])-1]
        dir=self.adj[RIGHT]//abs(self.adj[RIGHT])
        ret.extend(linepts(x,y,x,y+len,dir,shape))
        
        # Draw the bottom pattern
        x,y=self.x+len//2,self.y+len//2 # RD
        ret.append((x,y))

        shape=shape_lib[abs(self.adj[DOWN])-1]
        dir=self.adj[DOWN]//abs(self.adj[DOWN])
        ret.extend(linepts(x,y,x-len,y,dir,shape))
        
        # Draw the left pattern
        x,y=self.x-len//2,self.y+len//2 # LD
        ret.append((x,y))
        
        shape=shape_lib[abs(self.adj[LEFT])-1]
        dir=self.adj[LEFT]//abs(self.adj[LEFT])
        ret.extend(linepts(x,y,x,y-len,dir,shape))

        # If given screen, the tile will be drawn
        if type(screen)==pygame.Surface:
            pygame.draw.polygon(screen,colour, ret, stroke)

        return ret

class rect_grid: # board to display -- selection area and board area
    selected="green"
    deselected="white"
    def __init__(self, h: int, w: int, lb: int, ub: int, unit: int, colour: str | tuple = "white"):
        self.h=h
        self.w=w
        self.lb=lb
        self.ub=ub
        self.unit=unit
        self.grid=[[pygame.Rect(lb+i*unit,ub+j*unit,unit,unit) for i in range(w)] for j in range(h)] # create h*w rectangle objects
        self.colour=[[colour for i in range(w)] for j in range(h)]
    def select(self,pos): self.colour[pos[0]][pos[1]]=self.selected
    def deselect(self,pos): self.colour[pos[0]][pos[1]]=self.deselected

class button: # sometimes used as centralized text
    def __init__(self, text:str, fontname:str, fontsize: int, x: int, y: int, w: int=1, h: int=1, colour: str|None = None, stroke: int=0,stroke_colour: str|None=None,text_colour: str="Black"):
        self.font=pygame.font.SysFont(fontname, fontsize)
        self.rect=pygame.Rect(x-w//2,y-h//2,w,h)
        self.text=self.font.render(text, True, text_colour)
        self.textpos=self.text.get_rect(center=self.rect.center)
        if fontname=="avenirltproheavy" and not (pygame.font.match_font(fontname) is None): self.textpos.y+=fontsize//10 # looks like there is a bug with avenir font I got...
        self.colour=colour
        self.stroke=stroke
        self.stroke_colour=stroke_colour
        self.text_colour=text_colour
    def updatetext(self,text:str):
        self.text=self.font.render(text, True, self.text_colour)
        self.textpos=self.text.get_rect(center=self.rect.center)
    def plot(self,screen):
        '''Draw the button on given screen
        '''
        if self.colour!=None: pygame.draw.rect(screen, self.colour, self.rect,0)
        if self.stroke>0: pygame.draw.rect(screen, self.stroke_colour, self.rect,self.stroke)
        screen.blit(self.text,self.textpos)
    def clicked(self,Events):
        '''Check if the button is clicked in given events from pygame.event.get()
        '''
        for event in Events:
            if event.type != pygame.MOUSEBUTTONDOWN: continue
            if self.rect.collidepoint(event.pos): 
                return True
        return False

def empty_board(n: int, m: int)->Puzzle.board:
    '''Construct an n*m empty board
    '''
    return Tile.board([[Tile() for j in range(m)] for i in range(n)])

# The following functionsare GUI pages and the main function calling every page
# Returning -1 means the window is closed

def game(screen: pygame.Surface, level: int|dict, level_name: int|str)->int:
    '''
    Main game, return a status code for game's completion:
    -1: game window closed
    0: game completed
    1: user requested to go back to level selection
    '''
    # load level data
    if type(level)==int:
        with open('level.json', 'r') as file:
            level_dat = json.load(file)[level-1]
    if type(level)==dict: level_dat=level

    # game var
    n=level_dat["n"] # height
    m=level_dat["m"] # width
    orilist=level_dat["Tile"]
    board_size_tot=400
    board_size=board_size_tot//max(n,m)
    board_pos=(80,140)
    puzzle_size_tot=600
    puzzle_size=puzzle_size_tot//max(n,m)
    puzzle_pos=(600,60)
    tile=[] # selection
    puzzle=[] # board
    left=n*m

    # init game obj
    #  Tile & Board
    id=0
    for adj in orilist: 
        j,i=id//m+0.5,id%m+0.5
        tile.append(Tile(puzzle_pos[0]+i*puzzle_size,
                         puzzle_pos[1]+j*puzzle_size,
                         id,adj))
        puzzle.append(Tile(board_pos[0]+i*board_size,
                           board_pos[1]+j*board_size))
        id+=1
    orilist=deepcopy(tile)
    board=Puzzle.empty_board(n,m)

    #  Game operation buttons
    esc_button=button("Back"      ,'avenirltproheavy',32, 80, 50, 90,50,"white",1,"black")
    ls_button =button("<"         ,'avenirltproheavy',32,100,675, 50,50,"white",1,"black")
    rs_button =button(">"         ,'avenirltproheavy',32,250,675, 50,50,"white",1,"black")
    us_button =button("^"         ,'avenirltproheavy',32,175,600, 50,50,"white",1,"black")
    ds_button =button("v"         ,'avenirltproheavy',32,175,675, 50,50,"white",1,"black")
    lr_button =button("Rotate CCW",'avenirltproheavy',32,400,600,200,50,"white",1,"black")
    rr_button =button("Rotate CW" ,'avenirltproheavy',32,400,675,200,50,"white",1,"black")
    
    #  placing & selection area
    placing=rect_grid(n,m,board_pos[0],board_pos[1],board_size)
    selection=rect_grid(n,m,puzzle_pos[0],puzzle_pos[1],puzzle_size)

    #  win page
    gray_overlay=pygame.Surface((window_w, window_h))
    gray_overlay.fill((128,128,128))
    gray_overlay.set_alpha(0)
    win_text=button("You Win!",'avenirltproheavy',100,window_w//2,window_h//2,500,200,"white",2,"black")
    back_button=button("Back",'avenirltproheavy',32,window_w//2,window_h*4/5,90,50,"white",2,"black")

    #  level text
    font = pygame.font.SysFont('avenirltproheavy', 32)
    level_text=font.render(f"Level {level_name}", True, "Black")

    selector=(-1,-1)
    
    #  Solution management
    sol_button=button("Show Solution",'avenirltproheavy',32,350,50,250,50,"white",1,"black")
    sol=None
    show_sol=False

    while True:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        
        Events=pygame.event.get()
        if left>0: # process game input when game is actively running
            mouse_stat=(-1,)
            # status for the mouse
            # -1 = not clicked
            # 0 = clicked elsewhere
            # 1 = clicked board
            # 2 = clicked selection
            # 3 = clicked button (esc button would exit the game page immediately, with status code 1)
            for event in Events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mouse_stat[0]==-1: 
                        for i in range(n):
                            for j in range(m):
                                if placing.grid[i][j].collidepoint(event.pos):
                                    mouse_stat=(1,i,j)
                    if mouse_stat[0]==-1: 
                        for i in range(n):
                            for j in range(m):
                                if selection.grid[i][j].collidepoint(event.pos):
                                    mouse_stat=(2,i,j)
                    if mouse_stat[0]==-1: mouse_stat=(0,)
                if event.type == pygame.QUIT:
                    return EXIT
            if mouse_stat[0]!=-1: # Detect button
                if esc_button.clicked(Events): return 1 # exit the level
                # board shift request
                if us_button.clicked(Events): mouse_stat=(3,UP)
                if ds_button.clicked(Events): mouse_stat=(3,DOWN)
                if ls_button.clicked(Events): mouse_stat=(3,LEFT)
                if rs_button.clicked(Events): mouse_stat=(3,RIGHT)
                # board rotate request
                if lr_button.clicked(Events): mouse_stat=(3,10)
                if rr_button.clicked(Events): mouse_stat=(3,11)
                # solution triggered
                if sol_button.clicked(Events): mouse_stat=(3,20)

            if mouse_stat[0]!=-1: print(mouse_stat)
            
            # update state for objects
            if mouse_stat[0]==1:
                mouse_stat=mouse_stat[1:]
                if selector!=(-1,-1):
                    if board.fit(mouse_stat[0],mouse_stat[1],tile[selector[0]*m+selector[1]]): # can be put - swap pieces
                        # get the id for swapping
                        tileid=selector[0]*m+selector[1]
                        puzzleid=mouse_stat[0]*m+mouse_stat[1]
                        print(tileid,puzzleid)
                        # update tiles remaining
                        left-=puzzle[puzzleid].empty()
                        left+=tile[tileid].empty()
                        print(left)
                        # swap everything but position
                        puzzle[puzzleid],tile[tileid]=tile[tileid],puzzle[puzzleid]
                        puzzle[puzzleid].x,tile[tileid].x=tile[tileid].x,puzzle[puzzleid].x
                        puzzle[puzzleid].y,tile[tileid].y=tile[tileid].y,puzzle[puzzleid].y
                        # update the board
                        board.board[mouse_stat[0]][mouse_stat[1]]=puzzle[puzzleid]
                    else: # doesn't fit - give a warn
                        placing.colour[mouse_stat[0]][mouse_stat[1]]=(255,0,0)
                    selection.deselect(selector)
                    selector=(-1,-1)

            elif mouse_stat[0]==2:
                mouse_stat=mouse_stat[1:]
                if selector!=(-1,-1):
                    if selector!=mouse_stat: selection.deselect(selector)
                    else: tile[selector[0]*m+selector[1]]=tile[selector[0]*m+selector[1]].rotate()
                selector=mouse_stat
                selection.select(selector)
            
            elif mouse_stat[0]==3: 
                # 0~3: UP,RIGHT,DOWN,LEFT respectively
                # 10: rotate 90 deg counterclockwise 
                # 11: rotate 90 deg clockwise 
                # 20: show/hide solution
                if mouse_stat[1]==10: 
                    if board.issq(): 
                        board=board.rotate_board_90()
                        puzzle=[puzzle[(j)*m+(n-i-1)].rotate() for i in range(n) for j in range(m)]
                    else: 
                        board=board.rotate_board_180()
                        puzzle=[_.rotate().rotate() for _ in puzzle[::-1]]
                elif mouse_stat[1]==11: 
                    if board.issq(): 
                        for _ in range(3): # rotate 3*90
                            board=board.rotate_board_90()
                            puzzle=[puzzle[(j)*m+(n-i-1)].rotate() for i in range(n) for j in range(n)]
                    else: 
                        board=board.rotate_board_180()
                        puzzle=[_.rotate().rotate() for _ in puzzle[::-1]]
                elif mouse_stat[1]==20:
                    if sol==None: # Initialize solution
                        sol=Puzzle.solve(orilist,n,m)
                        if len(sol)<1: # No Solution
                            nosol_text=button("No Solution...", "avenirltproheavy", 80,board_pos[0]+board_size_tot//2,board_pos[1]+board_size_tot//2)
                        else: # Use the first returned solution
                            fs_sol=list(sol)[0]
                            print(f"{len(list(sol))} solution{("s" if len(list(sol))!=1 else "")} in total. The first one is shown below:")
                            # for i in list(sol): print(i)
                            print(fs_sol)
                            solution_tile=[]
                            # Initialize solution tiles
                            for i in range(n): 
                                for j in range(m): 
                                    cur=fs_sol.board[i][j]
                                    solution_tile.append(Tile(
                                        board_pos[0]+(j+0.5)*board_size,
                                        board_pos[1]+(i+0.5)*board_size,
                                        cur.id,cur.adj,"deepskyblue1"))
                    show_sol^=1
                    sol_button.updatetext(("Hide" if show_sol else "Show")+" solution")
                else:
                    _board=board.shift(mouse_stat[1])
                    if board!=_board:
                        board=_board # move the board
                        # Sync display with actual board
                        if mouse_stat[1]==UP   : puzzle=[puzzle[(i+1)*m+j] if i<n-1 else Tile(0,0) for i in range(n) for j in range(m)]
                        if mouse_stat[1]==DOWN : puzzle=[puzzle[(i-1)*m+j] if i>0   else Tile(0,0) for i in range(n) for j in range(m)]
                        if mouse_stat[1]==LEFT : puzzle=[puzzle[i*m+(j+1)] if j<m-1 else Tile(0,0) for i in range(n) for j in range(m)]
                        if mouse_stat[1]==RIGHT: puzzle=[puzzle[i*m+(j-1)] if j>0   else Tile(0,0) for i in range(n) for j in range(m)]

                # Add GUI pos for each of the new pieces
                for id in range(n*m): puzzle[id].x,puzzle[id].y=board_pos[0]+(id%m+0.5)*board_size,board_pos[1]+(id//m+0.5)*board_size

            elif mouse_stat[0]==0:
                if selector!=(-1,-1):
                    selection.deselect(selector)
                selector=(-1,-1)
        else: # At this stage the player has won the game, detect if back button is clicked
            if back_button.clicked(Events): return 0
        
        # update canvas
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")
        
        # draw puzzle
        screen.blit(level_text,(80,85))

        for i in range(n):
            for j in range(m):
                if type(placing.colour[i][j])==tuple:
                    # determine the colour of the grid if it's in the warning state
                    c=list(placing.colour[i][j])
                    # fade from red to white - G val and B val increse by 7 each frame
                    c[2]+=7
                    c[1]+=7
                    if c[1]<255 and c[2]<255: placing.colour[i][j]=tuple(c)
                    else: placing.colour[i][j]="white"
                pygame.draw.rect(screen, placing.colour[i][j], placing.grid[i][j],0)
                pygame.draw.rect(screen, "black", placing.grid[i][j],1)

        # Draw board
        for i in range(n):
            for j in range(m):
                pygame.draw.rect(screen, selection.colour[i][j], selection.grid[i][j],0)
                pygame.draw.rect(screen, "black", selection.grid[i][j],1)
        
        # Draw solution if requested
        if show_sol:
            if len(sol)<1:
                nosol_text.plot(screen)
            else:
                for i in range(n*m):
                    solution_tile[i].draw(board_size, screen, solution_tile[i].colour, 0)
                    solution_tile[i].draw(board_size, screen, "black", 1)

        # Draw tile in selection area
        for i in range(n*m):
            if tile[i].empty(): continue
            tile[i].draw(board_size, screen, tile[i].colour, 0)
            tile[i].draw(board_size, screen, "black", 1)
        
        # Draw tile in board
        for i in range(n*m):
            if puzzle[i].empty(): continue
            puzzle[i].draw(board_size, screen, puzzle[i].colour, 0)
            puzzle[i].draw(board_size, screen, "black", 1)
        
        # Draw buttons
        esc_button.plot(screen)
        ls_button.plot(screen)
        rs_button.plot(screen)
        us_button.plot(screen)
        ds_button.plot(screen)
        lr_button.plot(screen)
        rr_button.plot(screen)
        sol_button.plot(screen)

        if left<1: # win
            screen.blit(gray_overlay,(0,0))
            alpha=gray_overlay.get_alpha()
            if alpha<64: #fading process
                gray_overlay.set_alpha(alpha+2)
                pygame.time.delay(10) # Control fade speed
            else: #fading done
                win_text.plot(screen)
                back_button.plot(screen)
        
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

def level_choose(screen: pygame.Surface)->int:
    '''
    Run the GUI for choosing level
    Return -1 if window closed
    Otherwise return the level being chosen
    '''
    pygame.init()
    with open('level.json', 'r') as file: # get total number of levels
        level_cnt = len(json.load(file))
    esc=button("Back",'avenirltproheavy',32,80,50,90,50,"white",1,"black")
    level_button=[]
    for i in range(level_cnt): # init level buttons
        button_size=75
        button_space=120
        rcnt=8
        base_w=window_w//2-button_space*(rcnt-1)/2
        base_h=150
        level_button.append(button(str(i+1),'avenirltproheavy',32,
                                   base_w+i%rcnt*button_space,base_h+i//rcnt*button_space,
                                   button_size,button_size,
                                   "white",1,"black"))

    while True:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        Events=pygame.event.get()
        for event in Events:
            if event.type == pygame.QUIT:
                return EXIT

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")

        # RENDER YOUR GAME HERE
        esc.plot(screen)
        for i in range(level_cnt): level_button[i].plot(screen)
        
        # detect buttons
        if esc.clicked(Events): return 0
        for i in range(level_cnt): 
            if level_button[i].clicked(Events):
                return i+1
        
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

def main_pg(screen: pygame.Surface)->int:
    # button and text set up
    title=button("Impuzzable",'avenirltproheavy',100,window_w//2,window_h//4,525,100,text_colour="Red")
    playbutton=button("Play",'avenirltproheavy',32,window_w//2,window_h//2,200,40,"green",1,"black")
    warn4x4_1=button("The 4x4 random board"     ,'avenirltproheavy',32,window_w*3//4,window_h*7//8-20,text_colour="Red")
    warn4x4_2=button("won't guarantee a solution",'avenirltproheavy',32,window_w*3//4,window_h*7//8+20,text_colour="Red")
    size_txt=("3x3","3x4","4x4")
    randbutton=[]
    for i in range(3):
        randbutton.append(button(size_txt[i]+" Random",'avenirltproheavy',32,window_w*(i+1)//4,window_h*3//4,200,40,"deepskyblue1",1,"black"))
    while True:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        Events=pygame.event.get()
        for event in Events:
            if event.type == pygame.QUIT:
                return EXIT

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")

        # RENDER YOUR GAME HERE
        title.plot(screen)
        playbutton.plot(screen)
        warn4x4_1.plot(screen)
        warn4x4_2.plot(screen)
        for i in range(3): randbutton[i].plot(screen)
        for i in range(3): 
            if randbutton[i].clicked(Events):
                ld=button("Loading...",'avenirltproheavy', 32,window_w//2,window_h*7//8)
                ld.plot(screen)
                pygame.display.flip()
                return i+1
        # detect button being clicked
        if playbutton.clicked(Events): return 0
        
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
    

if __name__=="__main__":
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((window_w,window_h))
    clock = pygame.time.Clock()
    page=0
    state=0
    # calling pages
    while state!=EXIT:
        if page==0: # main pg
            state=main_pg(screen)
            if state==0: page=1
            else: page=3
        elif page==1: # level choose
            state=level_choose(screen)
            if state==0: page=0
            else: page=2
        elif page==2: # game page
            state=game(screen,state,state)
            page=1
        elif page==3: # random game + game page
            # Note that game generator is called in the main function
            modea=(3,3,4)
            modeb=(3,4,4)
            modec=(4,4,5)
            moded=(1,0,-1)
            # 3x3 board will guarantee an only solution, 3x4 board will guarantee a solution but not the only one
            # Due to the time complexity it takes to verify each solution, 4x4 board won't guarantee a solution
            state-=1
            import Generator
            data=Generator.GenData(modea[state],modeb[state],modec[state],moded[state])
            state=game(screen,data,f"%dx%d Random" %(modea[state],modeb[state]))
            page=0

    pygame.quit()