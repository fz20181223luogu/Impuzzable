'''
Generate levels for the puzzle Impuzzable
'''
from Puzzle import Tile, solve, UP, DOWN, LEFT, RIGHT
from random import randint
import time

class data:
    def __init__(self, n: int, m: int, p: int, distinct: bool=False):
        '''
        Calling a new data class will give game data for a n*m board with p different jigsaw patterns.
        Let distinct=True to avoid identical pieces. Note that Identical pieces placing swapping between different places will be count as different solutions.
        '''
        self.n=n
        self.m=m
        self.piece=[]
        for i in range(n*m):
            adj=[randint(1,p) for j in range(4)]
            # Format input so that concave in sides get negative value (Please don't use 0 for sides)
            if adj[DOWN]>0: adj[DOWN]=-adj[DOWN]
            if adj[LEFT]>0: adj[LEFT]=-adj[LEFT]
            if distinct:
                while Tile(i+1,adj) in self.piece:
                    adj=[randint(1,p) for j in range(4)]
                    if adj[DOWN]>0: adj[DOWN]=-adj[DOWN]
                    if adj[LEFT]>0: adj[LEFT]=-adj[LEFT]
            self.piece.append(Tile(i,adj))
    
    def __str__(self):
        '''
        Format test data in a way that Puzzle.py can accept
        simply print the data by print function to get the formatted data.
        '''
        ret=f"%d %d\n" %(self.n, self.m)
        for i in range(self.n*self.m):
            for j in range(4):
                ret+=str(self.piece[i].adj[j])
                if j==3: ret+='\n'
                else: ret+=' '
        return ret

def GenData(n: int,m: int,p: int, sol: int=-1):
    '''
    Generate a random data set consist of n rows, m columns and a maximum of p different patterns
    sol to guarantee solution status of data set:
    -1: no restriction, this is the default value
    0 or other negative integer: any number of solutions
    positive integer: maximum number of solutions
    It is strongly suggested to keep this value -1 when n*m>16
    '''
    t=0
    # Generating Data
    st_all=time.perf_counter()
    while True:
        # Generate
        t+=1
        print(f"Generating {t}th data set")
        s=data(n,m,p,True)
        if sol==-1: break
        # Solve
        print(f"Solving {t}th data set")
        st=time.perf_counter()
        ans=solve(s.piece,s.n,s.m)
        en=time.perf_counter()
        print(f"{len(ans)} solutions found for last data")
        print(f"Attempted {t} times, time used: {en-st}s")
        # Check if criteria met
        if ((sol<=0 and len(ans)>0) or 
            (sol>0 and 1<=len(ans)<=sol)): break
    en_all=time.perf_counter()
    print(f"A total of {t} data attempted to get desired data set, time used: {en_all-st_all}s")
    # Mapping data and return
    ret=dict()
    ret["n"]=s.n
    ret["m"]=s.m
    adj=[]
    for Tile in s.piece:
        adj.append(Tile.adj)
    ret["Tile"]=adj
    return ret

if __name__=="__main__":
    print("This program is a generator for the puzzle")
    print("If you see these text, you are running the generator of the puzzle instead of the game itself.")
    n,m,p,sol,num=map(int,input().split())
    ret=[]
    for i in range(num):ret.append(GenData(n,m,p,sol)["Tile"])
    for i in ret: print(i)