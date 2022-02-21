from pprint import pprint

from Solver.contraintes import CardinalityEQ,CardinalityLT, Equal, Intersection, Union, Inclusion
from Solver.ensemble import Ensemble

class FinRechercheException(Exception):
    pass


def filtrage(ensembles, contraintes):
    # reduction des domaines
    filtrage_ok = True
    modif = True
    while modif:
        modif = False
        for contrainte in contraintes:
            # si filtre = 0 alors pas de changement sur le domaine
            filtre = contrainte.filtre(ensembles)
            # si filtre = -1 alors la modification sur le domaine donne une inchoerance
            if filtre == -1:
                return False
            # si filtre = 1 alors la modification a modifie le domaine
            elif filtre == 1:
                modif = True
    return filtrage_ok


def sous_propagation(d, to_split, new_ensemble, old, new_contraintes, solutions, profondeur, une_solution):
    e = Ensemble(to_split.nom, domaine=d, const=True)
    new_ensemble[old] = e
    new_ens = []
    for v in new_ensemble:
        new_ens.append(v.duplicate())
    propagation(new_ens, new_contraintes, solutions, profondeur - 1 , une_solution=une_solution)


def tri_ensembles_contraintes(ensembles, contraintes):
    # liste_rank = [len(x.borneSup) - len(x.borneInf) for x in ensembles]
    liste_rank = [range(len(ensembles),-1) for x in ensembles]
    liste_noms = [x.nom for x in ensembles]
    _, nouvelle_liste_nom, new_ensemble = zip(*sorted(zip(liste_rank, liste_noms, ensembles)))
    new_ensemble = list(new_ensemble)
    new_contraintes = []
    for c in contraintes:
        new_contraintes.append(c.duplicate())
    for c in new_contraintes:
        if hasattr(c, 'var1'):
            c.var1 = nouvelle_liste_nom.index(liste_noms[c.var1])
            if hasattr(c, 'var2'):
                c.var2 = nouvelle_liste_nom.index(liste_noms[c.var2])
                if hasattr(c, 'var3'):
                    c.var3 = nouvelle_liste_nom.index(liste_noms[c.var3])
                    if hasattr(c, 'var4'):
                        c.var4 = nouvelle_liste_nom.index(liste_noms[c.var4])
    return new_ensemble, new_contraintes


def coupe(ensembles, contraintes, solutions, profondeur, une_solution=False):
    # S'il reste des ensembles non constants
    print("coup {}\t{}".format(ensembles,contraintes))
    if any([not v.const for v in ensembles]):
        # on trie les contraintes et ensembles et recupere le nouvel ensemble trie
        new_ensemble, new_contraintes = tri_ensembles_contraintes(ensembles, contraintes)

        # on recupere le prochain ensemble a couper et son indice dans le tableau des variables
        to_split = next(v for v in new_ensemble if not v.const)
        old = new_ensemble.index(to_split)

        if profondeur > 0:
	        for d in to_split.split():
	            # On propage avec le sous ensemble
	            print("sousprop {}\t{}".format(new_ensemble,new_contraintes))
	            sous_propagation(d, to_split, new_ensemble, old, new_contraintes,
	                             solutions, profondeur, une_solution)
        new_ensemble[old] = to_split


def verification_contraintes(ensembles, contraintes, solutions):
    # si toutes les ensembles sont des constantes
    if all([v.const for v in ensembles]):
        # on teste les contraintes
        return all([c.validation_contrainte(ensembles) for c in contraintes])
    return False


def propagation(ensembles, contraintes, solutions, profondeur, une_solution=False):
    # filtrage des ensembles
    print("prop {}\t{}".format(ensembles,contraintes))
    if filtrage(ensembles, contraintes):
        coupe(ensembles, contraintes, solutions, profondeur, une_solution=une_solution)
        # verification des contraintes
        if verification_contraintes(ensembles, contraintes, solutions):
            from copy import deepcopy
            solutions.append(deepcopy(ensembles))
            print(f'\n\tsolution {len(solutions)} : {ensembles}')
            if une_solution:
                raise FinRechercheException()


def get_num_var(variable, nom):
    for i, v in enumerate(variable):
        if v.nom == nom:
            return i
    raise Exception(f'Variable "{nom}" not found')

def Launch_Solver(sets,constraints, une_solution=False): # FlatBat 
	setobjs = []
	cstrobjs = []

	for s in sets:
		setobjs.append(Ensemble(s[0],domaine=s[1],const=s[2]))

	for c in constraints:
		if c[0]=="":
			print("unnamed constraint")
			return
		elif c[0]=="union":
			cstrobjs.append(Union(get_num_var(setobjs,c[3]),get_num_var(setobjs,c[1]),get_num_var(setobjs,c[2]),0))
		elif c[0]=="intersect":
			cstrobjs.append(Intersection(get_num_var(setobjs,c[3]),get_num_var(setobjs,c[1]),get_num_var(setobjs,c[2]),1))
		elif c[0]=="cardeq":
			cstrobjs.append(CardinalityEQ(get_num_var(setobjs,c[1]),get_num_var(setobjs,c[2]),0))
		elif c[0]=="cardlt":
			cstrobjs.append(CardinalityLT(get_num_var(setobjs,c[1]),get_num_var(setobjs,c[2]),0))
		elif c[0]=="existsIn":
			cstrobjs.append(Inclusion(get_num_var(setobjs,c[1]),get_num_var(setobjs,c[2]),5))
		elif c[0]=="equals":
			cstrobjs.append(Equal(get_num_var(setobjs,c[1]),get_num_var(setobjs,c[2]),10))


	solutions = []

	# cstrobjs.sort(key=lambda x: x.priorite, reverse=False)
	try:
		propagation(setobjs, cstrobjs, solutions, 50, une_solution=une_solution)
	except FinRechercheException as e:
		print(e)

	nb_solution = len(solutions)
	print(f'{nb_solution} solutions :')
	for i, sol in enumerate(solutions):
		print(sol)

	return solutions




if __name__ == "__main__":
	import time


	start_time = time.time()
	Launch_Solver(Ens,Cstr,True)
	print("--- %s seconds ---" % (time.time() - start_time))