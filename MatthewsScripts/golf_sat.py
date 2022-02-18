import numpy as np
import itertools
from pysat.solvers import Glucose3
g = Glucose3()

# Problem Dimentions and Ranges
W=4 	# num of weeks
G=5 	# num of groups
GS=3 	# group size
P=15 	# num of players # P=GGS


# Creating the Boolean Space
RB = 1 	# reserved Booleans #0 is always reserved -> RB>=1

_B4 = RB
B4_ = W*G*P*GS+_B4
B4 = np.array([b for b in range(_B4,B4_)],dtype=int).reshape((W,G,P,GS))

def combolist(size,triangle=True, diagonal=False):
	if(triangle):
		return [(i,j) for i,j in list(itertools.product(np.arange(size),np.arange(size))) if i<j]
	if(not diagonal):
		return [(i,j) for i,j in list(itertools.product(np.arange(size),np.arange(size))) if i!=j]
	return [(i,j) for i,j in list(itertools.product(np.arange(size),np.arange(size)))]



# A player plays at least once a week
for player in range(P):
	for week in range(W):
		OR = []
		for pos in range(GS):
			for group in range(G):
				OR += [int(B4[week,group,player,pos])]
		g.add_clause(OR)
		

# A player is once in a group
for player in range(P):
	for week in range(W):
		for group in range(G):
			for pos1, pos2 in combolist(GS):
				g.add_clause([int(-B4[week,group,player,pos1]),int(-B4[week,group,player,pos2])])
				

# A player plays once a week
for player in range(P):
	for week in range(W):
		for group1, group2 in combolist(G):
			# for pos1, pos2 in combolist(GS):
			for pos1 in range(GS):
				for pos2 in range(GS):
					g.add_clause([int(-B4[week,group1,player,pos1]),int(-B4[week,group2,player,pos2])])
					


# Groups have a player in each position
for week in range(W):
	for group in range(G):
		for pos in range(GS):
			OR = []
			for player in range(P):
				OR += [int(B4[week,group,player,pos])]
			g.add_clause(OR)


# One player per position
for week in range(W):
	for group in range(G):
		for pos in range(GS):
			for player1, player2 in combolist(P):
				g.add_clause([int(-B4[week,group,player1,pos]),int(-B4[week,group,player2,pos])])


# B4wgpp <-> B3wgp
_B3 = B4_+1
B3_ = _B3+W*G*P
B3 = np.array([b for b in range(_B3,B3_)],dtype=int).reshape((W,G,P))
for week in range(W):
	for group in range(G):
		for player in range(P):
			OR = [-int(B3[week,group,player])]
			for pos in range(GS):
				g.add_clause([-int(B4[week,group,player,pos]),int(B3[week,group,player])])
				OR += [int(B4[week,group,player,pos])]
			g.add_clause(OR)





# Players only meet each other once

couplesinP = len(combolist(P))
possibleMeets = G*W
# M
_M = B3_+1
M_ = _M+couplesinP*possibleMeets
M = np.array([b for b in range(_M,M_)],dtype=int).reshape((couplesinP,possibleMeets))

# For Each Couple, there is at most one PossibleMeet
for couple in range(couplesinP):
	for pm1, pm2 in combolist(possibleMeets):
		g.add_clause([-int(M[couple,pm1]),-int(M[couple,pm2])])

# B3wgp1 and B3wgp2 <-> M(p1*p2)(w*g)
# B3wgp1 and B3wgp2 -> M(p1*p2)(w*g) = -B3wgp1 -B3wgp2 M(p1*p2)(w*g)
# B3wgp1 and B3wgp2 <- M(p1*p2)(w*g) = 	B3wgp1 -M(p1*p2)(w*g)
#										B3wgp2 -M(p1*p2)(w*g)
wg=0
for week,group in [(i,j) for i,j in list(itertools.product(np.arange(W),np.arange(G)))]:	
	couple=0
	for player1, player2 in combolist(P):
		
		g.add_clause([-int(B3[week,group,player1]),-int(B3[week,group,player2]),int(M[couple,wg])])
		
		g.add_clause([int(B3[week,group,player1]),-int(M[couple,wg])])
		g.add_clause([int(B3[week,group,player2]),-int(M[couple,wg])])

		couple+=1
	wg+=1

 





print("{} variables".format(M_-1))
print(g.solve())

out = np.array(g.get_model()[_B3-1:B3_-1]).reshape(W,G,P)
for i, week in zip(range(len(out)),out):
	wstr="week {}\t".format(i)
	for j, group in zip(range(len(week)),week):
		wstr+="| ".format(j)
		gstr=""
		for k,player in zip(range(len(group)),group):
			if player>0:
				gstr+="{} ".format(k)
		wstr+=gstr+"\t"
	print(wstr)
