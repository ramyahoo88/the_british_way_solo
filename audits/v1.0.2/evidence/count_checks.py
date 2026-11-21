"""Count the bot's table work in simulated Agent games: goal checks and Special Activity checks per turn,
and how often the bot Passes. Usage: F136_CODE=<force136_v1/code> python3 count_checks.py [seeds]"""
import sys,os,collections
sys.path.insert(0,os.environ['F136_CODE'])
import force136_v1 as V
POLS=('extraction','hunting','repair','adaptive','counter','mixed')
class Count(V.Force136):
    def __init__(self,*a,**k):
        V.Force136.__init__(self,*a,**k);self.c=Box()
    def goal(self,name,full):
        if not self.preview:self.c.n['goal checks']+=1
        return V.Force136.goal(self,name,full)
    def sa_does(self,p,x):
        if not self.preview:self.c.n['SA checks']+=1
        return V.Force136.sa_does(self,p,x)
    def bot_turn(self,free):
        V.Force136.bot_turn(self,free)
        if not self.preview:
            self.c.n['turns']+=1
            if self.last_plan['op']=='PASS':self.c.n['passes']+=1
class Box:
    def __init__(self):self.n=collections.Counter()
if __name__=='__main__':
    n=int(sys.argv[1]) if len(sys.argv)>1 else 100
    tot=collections.Counter()
    for seed in range(n):
        for p in POLS:
            g=Count(seed);g.policy=p;g.run();tot.update(g.c.n);tot['games']+=1
    print(dict(tot))
    print('goal checks per turn',round(tot['goal checks']/tot['turns'],2),'| SA checks per turn',round(tot['SA checks']/tot['turns'],2),
          '| turns per game',round(tot['turns']/tot['games'],1),'| Pass share',round(100*tot['passes']/tot['turns'],2),'%')
