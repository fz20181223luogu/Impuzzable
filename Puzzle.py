'''
Ver. 1.0: Bug fixes as a published version

Ver. 0.4: Let board become a class

Ver. 0.3: Optimized the way of eliminate duplication as well as searching result, added progress when solving the puzzle

Ver. 0.2: Added elimination of duplication (with ChatGPT help me to hash Tile class so that set can help eliminate duplicate items)

This program takes in n*m pieces of tiles which each of them has 2 sides concave out and 2 sides concave in.
The sides with concave out will be assigned a positive value, while the sides with concave in will be assigend a negative value.
If two sides can match each other, they share the same absolute value (i.e. the sum of two sides is zero)
The program will output all possible solutions to let those tiles form a n by m rectangle, or prompt no solution if impossible.
'''
from __future__ import annotations
from copy import deepcopy
UP,RIGHT,DOWN,LEFT=0,1,2,3 # Adjacent cell array order assignment
# By default up and right are concave out, down and left are concave in
# +---------------------+
# |                     |
# |       adj[0]        |
# |        (+)          |
# |                     |
# |adj[3]        adj[1] |
# | (-)           (+)   |
# |                     |
# |       adj[2]        |
# |        (-)          |
# +---------------------+

class Tile:
    def __init__(self, id: int = -1, adj: list = [0,0,0,0]):
        self.id=id # Default to be -1 (empty)
        self.adj=adj[:]
        
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.adj == other.adj

    def __hash__(self):
        # Convert adj to a tuple so it's hashable
        return hash((self.id, tuple(self.adj)))

    def __repr__(self):
        '''visualize tile in CLI
        '''
        return ("+--------+\n"+
               f"|   %02d   |\n" % self.adj[UP]+
               f"|%02d %02d %02d|\n" % (self.adj[LEFT],self.id,self.adj[RIGHT])+
               f"|   %02d   |\n" % self.adj[DOWN]+
                "+--------+")
    
    def rotate(self):
        '''Rotate current tile 90 degrees anticlockwise
        '''
        return Tile(self.id,[self.adj[(i+1)%4] for i in range(4)])
    
    def empty(self):
        '''Detect if current tile is empty (default tile)
        '''
        return self.id==-1

class board:
    def __init__(self,board: list[list[Tile]]):
        self.board=board
        self.h=len(board)
        self.w=len(board[0])

    def issq(self): 
        '''Detect if given board is a square (which height==width)
        '''
        return (self.h==self.w)
    
    def __hash__(self):
        # Convert tiles to a tuple so it's hashable
        return hash(tuple(tuple(cell for cell in row) for row in self.board))
    
    def __eq__(self, other):
        if not isinstance(other, board):
            return False
        return tuple(tuple(cell for cell in row) for row in self.board)==tuple(tuple(cell for cell in row) for row in other.board)

    def __repr__(self):
        '''visualize board in CLI
        '''
        ret=""
        for row in self.board:
            for j in range(len(row)): ret+="+--------"
            ret+="+\n"
            for piece in row: ret+=(f"|   %02d   " % piece.adj[UP])
            ret+="|\n"
            for piece in row: ret+=(f"|%02d %02d %02d" % (piece.adj[LEFT],piece.id,piece.adj[RIGHT]))
            ret+="|\n"
            for piece in row: ret+=(f"|   %02d   " % piece.adj[DOWN])
            ret+="|\n"
        for j in range(len(row)): ret+="+--------"
        ret+="+"
        return ret

    def fit(self, x:int, y:int, t:Tile)-> bool:
        '''
        Check if tile t can fit in (x,y) based on current situation
        nomatter if there is a tile at (x,y)
        '''
        if t.empty(): return True # empty block fits everything
        if x>0: # fit up
            if not self.board[x-1][y].empty():
                if self.board[x-1][y].adj[DOWN]+t.adj[UP]!=0: return False
        if x<self.h-1: # fit down
            if not self.board[x+1][y].empty():
                if self.board[x+1][y].adj[UP]+t.adj[DOWN]!=0: return False
        if y>0: # fit left
            if not self.board[x][y-1].empty():
                if self.board[x][y-1].adj[RIGHT]+t.adj[LEFT]!=0: return False
        if y<self.w-1: # fit right
            if not self.board[x][y+1].empty():
                if self.board[x][y+1].adj[LEFT]+t.adj[RIGHT]!=0: return False
        return True

    # Board transform
    def rotate_board_90(self)-> board:
        '''Rotate a square (which width is equal to height) board 90 degrees anticlockwise
        If the board is not a square, return the board itself
        '''
        if not self.issq(): return self
        return board([[self.board[j][len(self.board)-i-1].rotate() for j in range(self.w)] for i in range(self.h)])
    
    def rotate_board_180(self)-> board:
        '''Rotate a board 180 degrees
        '''
        return board([[self.board[len(self.board)-i-1][len(self.board[0])-j-1].rotate().rotate() for j in range(self.w)] for i in range(self.h)])

    def shift(self,dir:int)-> board:
        '''
        shift the entire board to a certain direction 1 unit (if possible)
        direction defined by constant at the beginning
        '''
        n,m=self.h,self.w
        ret=empty_board(n,m)
        if dir==UP: 
            for j in range(m):
                if not self.board[0][j].empty(): return self # shift not available
                for i in range(1,n): ret.board[i-1][j]=self.board[i][j]
        if dir==DOWN: 
            for j in range(m):
                if not self.board[n-1][j].empty(): return self # shift not available
                for i in range(0,n-1): ret.board[i+1][j]=self.board[i][j]
        if dir==LEFT: 
            for i in range(n):
                if not self.board[i][0].empty(): return self # shift not available
                for j in range(1,m): ret.board[i][j-1]=self.board[i][j]
        if dir==RIGHT: 
            for i in range(n):
                if not self.board[i][m-1].empty(): return self # shift not available
                for j in range(0,m-1): ret.board[i][j+1]=self.board[i][j]
        return ret

def empty_board(n: int, m: int)->board:
    '''Construct an n*m empty board
    '''
    return board([[Tile() for j in range(m)] for i in range(n)])

def solve(piece: list[Tile], n: int, m: int, prog: bool=False)-> set[board]:
    '''
    Search possible solutions to complete the puzzle with n rows and m columns
    Pieces are given by the parameter piece
    prog will output approximate progress, based on which tile is being tried on the first cell.
    '''
    global ans
    ans=set()
    def dfs(game: board, vis: list, piece: list[Tile], x: int, y: int, prog: bool=False)-> set[board]:
        '''
        dfs part
        '''
        n,m=game.h,game.w # Get the width(m) and height(n) of the board
        if x==n:# If all tiles are filled, then success
            global ans
            ans.add(deepcopy(game))
        
        st,en=0,n*m
        if game.issq():
            if (x==0 and y==m-1) or (x==n-1 and y==0) or(x==n-1 and y==m-1):
                st=game.board[0][0].id # corner tile ID no less than top-left tile ID
            if x==0 and y==0: 
                en-=3 # Top-left ID cannot be greater than n*m-3 to accomodate other corners -- faster
        else:
            if (x==n-1 and y==m-1):
                st=game.board[0][0].id # bottom-right tile ID no less than top-left tile ID
            if x==0 and y==0: 
                en-=1 # Top-left ID cannot be greater than n*m-1 to accomodate bottom-right corners -- faster
        # print(x,y,st,en)
        # print(game)
        # garbage=input() # calls a breakpoint manually
        for i in range(st,en):
            if prog: print(f"Progress: {(i*100)//(en-st)}%") # Progress based on first tile's ID searching
            if vis[i]: continue # If used, skip the current tile
            cur=piece[i]
            vis[i]=True # Use and mark the current tile
            for j in range(4): # Try different rotations
                if game.fit(x,y,cur): # Check if this rotation fit
                    game.board[x][y]=cur # Use that in tile and move on to the next one
                    nx=x # move on to the next tile
                    ny=y+1
                    if ny==m:
                        ny=0
                        nx+=1
                    dfs(game,vis,piece,nx,ny,0)
                    game.board[x][y]=Tile() # Reset current tile
                cur=cur.rotate()
            vis[i]=False # Unmark
    
    dfs(empty_board(n,m), # empty board
        [False for i in range(n*m)], # empty visit state
        piece, # piece used to fill
        0, 0, # starting top-left
        prog) 
    return ans

if __name__=="__main__":
    print("This program is a solver as well as a library for the puzzle")
    print("If you see these text, you are running the solver of the puzzle instead of the game itself.")
    n,m=map(int,input().split())
    piece=[]
    for i in range(n*m):
        adj=list(map(int,input().split()))
        # Format input so that concave in sides get negative value (Please don't use 0 for sides)
        if adj[UP]<0: adj[UP]=-adj[UP]
        if adj[RIGHT]<0: adj[RIGHT]=-adj[RIGHT]
        if adj[DOWN]>0: adj[DOWN]=-adj[DOWN]
        if adj[LEFT]>0: adj[LEFT]=-adj[LEFT]
        piece.append(Tile(i,adj))
    # for i in piece: print(i)
    ans=solve(piece,n,m,True)
    if len(ans)==0:
        print("No Solutions")
    else:
        for i in range(len(ans)): 
            print(f"Solution {i+1}:")
            print(list(ans)[i])