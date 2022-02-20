from copy import copy
from math import pow


class Ensemble:

    def __init__(self, nom, domaine=None, const=False):
        self.nom = nom
        self.const = const
        if domaine is None:
            domaine = set()
        self.value = None
        if const:
            if type(domaine) == int:
                self.borneInf = set()
                self.borneSup = set()
                self.value = domaine
            else:
                self.borneInf = domaine
                self.borneSup = domaine
        else:
            self.borneInf = set()
            self.borneSup = domaine

    def valide(self):
        for element in self.borneInf:
            if element not in self.borneSup:
                return False
        return True

    def duplicate(self):
        if self.value is not None:
            return Ensemble(str(self.nom), self.value, const=bool(self.const))
        new_ensemble = Ensemble(str(self.nom), {}, const=bool(self.const))

        new_borne_inf = set()
        for i in self.borneInf:
            new_borne_inf.add(i)
        new_ensemble.borneInf = new_borne_inf
        new_borne_sup = set()
        for i in self.borneSup:
            new_borne_sup.add(i)
        new_ensemble.borneSup = new_borne_sup
        return new_ensemble

    def split(self):
        if self.value is None:
            ens = list(self.borneSup - self.borneInf)
            size_ens = len(ens)
            for a in range(int(pow(2, size_ens))):
                s = str(size_ens)
                ss = '{0:0' + s + 'b}'
                ss = ss.format(a)
                el = []
                for i, j in enumerate(ss):
                    if j == "1":
                        el.append(ens[i])
                yield copy(self.borneInf.union(set(el)))
        else:
            return [self.value]

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.const:
            return f'{self.nom} = {self.borneInf}'
        else:
            return f'{self.nom} = Borne Inf : {self.borneInf} -- Borne Sup : {self.borneSup}'

    def __eq__(self, other):
        return self.borneInf == other.borneInf and self.borneSup == other.borneSup
