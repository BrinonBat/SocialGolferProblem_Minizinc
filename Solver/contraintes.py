from abc import ABC, abstractmethod


class Contrainte(ABC):

    def __init__(self, contrainte, priorite):
        self.contrainte = contrainte
        self.priorite = priorite

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.contrainte

    @abstractmethod
    def validation_contrainte(self, ensembles):
        pass

    @abstractmethod
    def filtre(self, ensembles):
        pass

    @abstractmethod
    def duplicate(self):
        pass


class ContrainteBinaire(Contrainte, ABC):

    def __init__(self, contrainte, var1, var2, priorite):
        super().__init__(contrainte, priorite)
        self.var1 = var1
        self.var2 = var2

    def __str__(self):
        return str(self.var1) + self.contrainte + str(self.var2)


class Different(ContrainteBinaire):

    def __init__(self, var1, var2, priorite):
        super().__init__(" != ", var1, var2, priorite)

    def validation_contrainte(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        return var1.borneInf != var2.borneInf

    def filtre(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        if var1.const and var2.const:
            if var1.borneInf == var2.borneInf:
                return -1
        return 0

    def duplicate(self):
        return Different(self.var1, self.var2, self.priorite)


class Equal(ContrainteBinaire):

    def __init__(self, var1, var2, priorite):
        super().__init__(" = ", var1, var2, priorite)

    def validation_contrainte(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        return var1.borneInf == var2.borneInf

    def filtre(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        if var1.const and var2.const:
            if var1.borneInf != var2.borneInf:
                return -1
        if var2.const and not var1.const:
            var1.borneInf = var2.borneInf
            var1.borneSup = var1.borneInf
            var1.const = True
            return 1
        if var1.const and not var2.const:
            var2.borneInf = var1.borneInf
            var2.borneSup = var2.borneInf
            var2.const = True
            return 1
        return 0

    def duplicate(self):
        return Equal(self.var1, self.var2, self.priorite)


class CardinalityEQ(ContrainteBinaire):

    def __init__(self, var1, var2, priorite):
        super().__init__(" cardinality =  ", var1, var2, priorite)

    def validation_contrainte(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        return (len(var1.borneInf) <= var2.value) and (len(var1.borneSup) >= var2.value)

    def filtre(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        if var1.const:
            if len(var1.borneInf) != var2.value:
                return -1
        return 0

    def duplicate(self):
        return CardinalityEQ(self.var1, self.var2, self.priorite)

class CardinalityLT(ContrainteBinaire):

    def __init__(self, var1, var2, priorite):
        super().__init__(" cardinality <  ", var1, var2, priorite)

    def validation_contrainte(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        return (len(var1.borneInf) < var2.value)

    def filtre(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        if var1.const:
            if len(var1.borneInf) >= var2.value:
                return -1
        return 0

    def duplicate(self):
        return CardinalityLT(self.var1, self.var2, self.priorite)


class Inclusion(ContrainteBinaire):

    def __init__(self, var1, var2, priorite):
        super().__init__(" Inclusion ", var1, var2, priorite)

    def validation_contrainte(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        return all([e in var2.borneInf for e in var1.borneInf])

    def filtre(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        var1tmp = var1.duplicate()
        var2tmp = var2.duplicate()

        # if not var1.const:
        var1.borneSup &= var2.borneSup
        # if not var2.const:
        var2.borneInf |= var1.borneInf

        if not (var1.valide() and var2.valide()):
            return -1
        return int(var1 != var1tmp or var2 != var2tmp)

    def duplicate(self):
        return Inclusion(self.var1, self.var2, self.priorite)


class Exclusion(ContrainteBinaire):

    def __init__(self, var1, var2, priorite):
        super().__init__(" Exclusion ", var1, var2, priorite)

    def validation_contrainte(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        return all([e not in var2.borneInf for e in var1.borneInf])

    def filtre(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        var1tmp = var1.duplicate()
        var2tmp = var2.duplicate()

        var1.borneSup &= var2.borneSup
        var2.borneInf |= var1.borneInf

        var1.borneSup -= var2.borneInf
        var2.borneSup -= var1.borneInf

        if not (var1.valide() and var2.valide()):
            return -1
        return int(var1 != var1tmp or var2 != var2tmp)

    def duplicate(self):
        return Exclusion(self.var1, self.var2, self.priorite)


class ContrainteTernaire(Contrainte, ABC):

    def __init__(self, contrainte, var1, var2, var3, priorite):
        super().__init__(contrainte, priorite)
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3

    def __str__(self):
        return str(self.var1) + " = " + str(self.var2) + self.contrainte + str(self.var3)


class Union(ContrainteTernaire):

    def __init__(self, var1, var2, var3, priorite):
        super().__init__(" Union ", var1, var2, var3, priorite)

    def validation_contrainte(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        var3 = ensembles[self.var3]
        return var1.borneInf == var2.borneInf.union(var3.borneInf)

    def filtre(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        var3 = ensembles[self.var3]
        var1tmp = var1.duplicate()
        
        # if not var1.const:
        var1.borneInf |= (var2.borneInf | var3.borneInf)
        var1.borneSup &= (var2.borneSup | var3.borneSup)

        # if not var2.const:
        #     var2.borneInf |= (var1.borneInf - var3.borneInf)
        #     # var2.borneSup &= (var2.borneSup | var3.borneSup)
        # if not var3.const:
        #     var3.borneInf |= (var1.borneInf - var2.borneInf)

        if not var1.valide():
            return -1
        return int(var1 != var1tmp)

    def duplicate(self):
        return Union(self.var1, self.var2, self.var3, self.priorite)


class Intersection(ContrainteTernaire):

    def __init__(self, var1, var2, var3, priorite):
        super().__init__(" Intersection ", var1, var2, var3, priorite)

    def validation_contrainte(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        var3 = ensembles[self.var3]
        return var1.borneInf == var2.borneInf.intersection(var3.borneInf)

    def filtre(self, ensembles):
        var1 = ensembles[self.var1]
        var2 = ensembles[self.var2]
        var3 = ensembles[self.var3]
        var1tmp = var1.duplicate()
        var2tmp = var2.duplicate()
        var3tmp = var3.duplicate()

        # if not var1.const:
        var1.borneInf |= (var2.borneInf & var3.borneInf)
        
        # if not var2.const:
        var2.borneInf |= var1.borneInf
        # var2.borneSup -= (var3.borneSup - var1.borneSup)

        # if not var3.const:
        var1.borneSup &= (var2.borneSup & var3.borneSup)
        var3.borneInf |= var1.borneInf
        # var3.borneSup -= (var2.borneSup - var1.borneSup)
        

        if not (var1.valide() and var2.valide() and var3.valide()):
            return -1
        return int(var1 != var1tmp or var2 != var2tmp or var3 != var3tmp)

    def duplicate(self):
        return Intersection(self.var1, self.var2, self.var3, self.priorite)
