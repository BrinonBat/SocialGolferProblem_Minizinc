from pprint import pprint

from contraintes import Cardinalite, Different, Egal, Intersection, Intersection3
from ensemble import Ensemble

def get_num_var(variable, nom):
    for i, v in enumerate(variable):
        if v.nom == nom:
            return i
    raise Exception(f'Variable "{nom}" not found')

def Launch_Solver(sets,constraints, instancesettings): # Format Baptist 
	setobjs = []
	cstrobjs = []

	for s in sets:
		pass
		# setobjs.append(Ensemble())

	for c in constraints:
		if c[0]=="":
			print("unnamed constraint")
			return
		elif c[0]=="union":
			cstrobjs.append(Union(get_num_var(setobjs,c[1]),get_num_var(setobjs,c[2]),get_num_var(setobjs,c[3])))
		elif c[0]=="intersection":
			cstrobjs.append(Intersection(get_num_var(setobjs,c[1]),get_num_var(setobjs,c[2]),get_num_var(setobjs,c[3])))
		elif c[0]=="Card":
			cstrobjs.append(Cardinalite(get_num_var(setobjs,c[1],c[2],c[3])))
