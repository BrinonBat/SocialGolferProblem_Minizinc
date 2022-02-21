from copy import deepcopy
from sre_compile import isstring
import re
from ui import WindowManager
from Solver.setsolver import Launch_Solver


def isSet(model,attribute):
    if str(getattr(model,attribute)).__contains__('..'): return True
    return False
   
def isVariable(model,attribute):
    string=str(getattr(model,attribute))
    if isstring(string) and attribute!='resolution':
        if not string.__contains__('..'):
            if not string.__contains__('['):
                return True
    return False

def hasANonNumeric(model):
    for attribute in model.__dict__:
        if(isVariable(model,attribute)):

            if not str(getattr(model,attribute)).isnumeric(): 
                return True
    return False

def replaceString(model,phrase):
    for attribute in model.__dict__:
        if isstring(getattr(model,attribute)):
            phrase=phrase.replace(attribute,str(getattr(model,attribute)))
    
    return phrase

def calculateString(string):
    try: 
        result=eval(string)
    except ValueError:
        pass
    return str(result)

def calculateVariables(model):
    remaining=20 # security, maximum number of iterations
    while(hasANonNumeric(model)):
        if(remaining<0): break
        for attribute in model.__dict__:
            if(isVariable(model,attribute)) and attribute !='resolution':
                #le mets à jour si besoin
                if not (getattr(model,attribute).isnumeric()):
                    replaced=replaceString(model,getattr(model,attribute))
                    replaced=calculateString(replaced)
                    setattr(model,attribute,replaced)
        remaining-=1
        print("remaining : "+str(remaining))

def replaceStringOnSet(model,contrainte):
    for i in range(0,len(contrainte)):
        if isstring(contrainte[i]):
            contrainte[i]=replaceString(model,contrainte[i])
        else:
            contrainte[i]=replaceStringOnSet(model,contrainte[i])
    return contrainte
    
def extractNumbers(strings):
    strings=''.join(strings)
    if(strings.__contains__('..')): strings.replace('..','_to_')
    if(strings.__contains__('_to_')):
        numbers=strings.split('_to_')
        li_numbers=list(range(int(numbers[0]),int(numbers[1])+1))

    else:li_numbers=[int(s) for s in re.findall(r'-?\d+', strings)]

    return li_numbers

def replaceByValues(contrainte,dico):
    for i in range(0,len(contrainte)):
        if isstring(contrainte[i]):
            for var in dico:
                contrainte[i]=contrainte[i].replace(var,str(dico[var]))
        else:
            contrainte[i]=replaceByValues(contrainte[i],dico)
    return contrainte

def dicoUpdate(dico,mat_values):
    for i in range(len(dico)-1,-1,-1):
    
        if(dico[mat_values[i][0]]==mat_values[i][1][-1]):
            dico[mat_values[i][0]]=mat_values[i][1][0] #réinitialisation à la première valeur
            #print("dernier element, incrémentation de la valeur précédante")
        else: 
            indice=mat_values[i][1].index(dico[mat_values[i][0]])
            dico[mat_values[i][0]]=mat_values[i][1][indice+1]
            return dico

def testIteration(contrainte):
    if(contrainte[0]=="equals"):
        return contrainte[1]==contrainte[2]
    elif(contrainte[0]=="notEquals"):
        return contrainte[1]!=contrainte[2]

def atomiseContrainte(contrainte,li_contraintes):
    if contrainte[0]=="forall":
        #prise en compte des paramètres sur lesquels boucler
        mat_values=[]
        for parameters in contrainte[1]:
            parameters=parameters.split()
            mat_values.append([parameters[0],extractNumbers(parameters[2:])])
        #print(mat_values)
                    
        #initialisation du dictionnaire de suivi des valeurs
        dico_parameters={}
        for elem in mat_values:
            dico_parameters[elem[0]]=elem[1][0]

        #remplacement en boucle dans la suite
        total_iter=1 #compte le nombre d'iterations
        for elem in mat_values:
            total_iter=total_iter*len(elem[1])


        while(total_iter>0):
            total_iter=total_iter-1
            #print("total_iter is "+str(total_iter))
            #modifie une copie de la contrainte
            copy_contrainte=deepcopy(contrainte)
            copy_contrainte=replaceByValues(copy_contrainte,dico_parameters)
            #print("dico_parameters AVANT : "+str(dico_parameters))
            if(total_iter>1) : dico_parameters=dicoUpdate(dico_parameters,mat_values)
            #print("dico_parameters APRES : "+str(dico_parameters))
            #relance de l'algo sur la contrainte modifiée
            #cas où un where est dans la boucle
            if(contrainte[2][0]=="where"):
                if not testIteration(copy_contrainte[2][1]): pass
                else : li_contraintes.append(atomiseContrainte(copy_contrainte[3],li_contraintes))
            else: li_contraintes.append(atomiseContrainte(copy_contrainte[2],li_contraintes))

    elif contrainte[0]=="equals":
        if not isstring(contrainte[1]):
            if contrainte[1][0]=="card":
                contrainte[0]="cardeq"
                contrainte[1]=atomiseContrainte(contrainte[1][1],li_contraintes)
            else: contrainte[1]=atomiseContrainte(contrainte[1],li_contraintes)
        else:
            if contrainte[1].__contains__('..'):
                tmp=contrainte[1].split('..')
                contrainte[1]=str((eval(tmp[0])))+'_to_'+str(eval(tmp[1]))
        
        if not isstring(contrainte[2]):
            if contrainte[2][0]=="card":
                contrainte[0]="cardeq"
                contrainte[2]=atomiseContrainte(contrainte[2][1],li_contraintes)
            else: contrainte[2]=atomiseContrainte(contrainte[2],li_contraintes)
        else:
            if contrainte[2].__contains__('..'):
                tmp=contrainte[2].split('..')
                contrainte[2]=str((eval(tmp[0])))+'_to_'+str(eval(tmp[1]))
        
        li_contraintes.append(contrainte)

    elif contrainte[0]=="lesserThan":
        if not isstring(contrainte[1]):
            if contrainte[1][0]=="card":
                contrainte[0]="cardlt"
                contrainte[1]=atomiseContrainte(contrainte[1][1],li_contraintes)
            else: contrainte[1]=atomiseContrainte(contrainte[1],li_contraintes)
        else:
            if contrainte[1].__contains__('..'):
                tmp=contrainte[1].split('..')
                contrainte[1]=list(range(eval(tmp[0]),eval(tmp[1])+1))
        
        if not isstring(contrainte[2]):
            if contrainte[2][0]=="card":
                contrainte[0]="cardlt"
                contrainte[2]=atomiseContrainte(contrainte[2][1],li_contraintes)
            else: contrainte[2]=atomiseContrainte(contrainte[2],li_contraintes)
        else:
            if contrainte[2].__contains__('..'):
                tmp=contrainte[2].split('..')
                contrainte[2]=list(range(eval(tmp[0]),eval(tmp[1])+1))
        
        li_contraintes.append(contrainte)

    elif contrainte[0]=="greaterThan":
        if not isstring(contrainte[1]):
            if contrainte[1][0]=="card":
                contrainte[0]="cardgt"
                contrainte[1]=atomiseContrainte(contrainte[1][1],li_contraintes)
            else: contrainte[1]=atomiseContrainte(contrainte[1],li_contraintes)
        else:
            if contrainte[1].__contains__('..'):
                tmp=contrainte[1].split('..')
                contrainte[1]=list(range(eval(tmp[0]),eval(tmp[1])+1))
        
        if not isstring(contrainte[2]):
            if contrainte[2][0]=="card":
                contrainte[0]="cardgt"
                contrainte[2]=atomiseContrainte(contrainte[2][1],li_contraintes)
            else: contrainte[2]=atomiseContrainte(contrainte[2],li_contraintes)
        else:
            if contrainte[2].__contains__('..'):
                tmp=contrainte[2].split('..')
                contrainte[2]=list(range(eval(tmp[0]),eval(tmp[1])+1))
        
        li_contraintes.append(contrainte)
  
    elif contrainte[0]=="array_union":
        #prise en compte des paramètres sur lesquels boucler
        mat_values=[]
        for parameters in contrainte[1]:
            parameters=parameters.split()
            mat_values.append([parameters[0],extractNumbers(parameters[2:])])
        #print(mat_values)
                    
        #initialisation du dictionnaire de suivi des valeurs
        dico_parameters={}
        for elem in mat_values:
            dico_parameters[elem[0]]=elem[1][0]

        #remplacement en boucle dans la suite
        total_iter=1 #compte le nombre d'iterations
        for elem in mat_values:
            total_iter=total_iter*len(elem[1])
        
        
        copy_contrainte=deepcopy(contrainte)
        copy_contrainte=replaceByValues(copy_contrainte,dico_parameters)
        part1=deepcopy(copy_contrainte[2])
        dico_parameters=dicoUpdate(dico_parameters,mat_values)
        copy_contrainte=deepcopy(contrainte)
        copy_contrainte=replaceByValues(copy_contrainte,dico_parameters)
        part2=deepcopy(copy_contrainte[2])
        nom_var='uc'+''.join(map(str,extractNumbers(part1)))+''.join(map(str,extractNumbers(part2)))
        union_contraintes=[['union',part1,part2,nom_var]]
        i=0
        while(total_iter-i>2):
            if(i+1<total_iter) : dico_parameters=dicoUpdate(dico_parameters,mat_values)
            copy_contrainte=deepcopy(contrainte)
            copy_contrainte=replaceByValues(copy_contrainte,dico_parameters)
            part2=deepcopy(copy_contrainte[2])
            part1=union_contraintes[i][3]
            nom_var='uc'+''.join(map(str,extractNumbers(part1)))+''.join(map(str,extractNumbers(part2)))
            union_contraintes.append(['union',part1,part2,nom_var])
            i+=1
        li_contraintes+=union_contraintes
        #return uniquement sur la toute dernière valeur
        return union_contraintes[-1][3]

    elif contrainte[0]=="intersect":
    
        part1=deepcopy(contrainte[1])
        part2=deepcopy(contrainte[2])
        nom_var='_'.join(map(str,extractNumbers(part1)))+'n'+'_'.join(map(str,extractNumbers(part2)))
        nom_var_inverse='_'.join(map(str,extractNumbers(part2)))+'n'+'_'.join(map(str,extractNumbers(part1)))
        if not (['intersect',part2,part1,nom_var_inverse] in li_contraintes):
            res=[['intersect',part1,part2,nom_var]]
            li_contraintes+=res
            return nom_var
        return None

    elif contrainte[0]=="existsIn":
        part1=deepcopy(contrainte[1])
        part2=deepcopy(contrainte[2])
        res=[['existsIn',part1,part2]]
        li_contraintes+=res

    else: return contrainte


#le modèle ici est déjà complet. Les variables ont été saisies au préalable par l'utilisateur à laide des méthodes suviantes:
def instanciate(self, model):

    new_variables=[]
    default_domain={}
    #maj valeurs variables
    calculateVariables(model)

    #maj des sets
    for attribute in model.__dict__:
        if attribute !='resolution' and attribute!='constraints':
            if isSet(model,attribute): #uniquement pour les sets
                new_one=replaceString(model,getattr(model,attribute))
                new_one=new_one.split('..')
                new_one=str(new_one[0])+'_to_'+str(new_one[1])
                setattr(model,attribute,new_one)

        if attribute=='golfeurs':
            numbers=getattr(model,attribute).split('_to_')
            default_domain=set(list(range(int(numbers[0]),int(numbers[1])+1)))
    #affichage du modèle
    #for attribute in model.__dict__:
    #    if attribute !='resolution' and attribute!='constraints':
    #        print(str(attribute)+" : "+str(getattr(model,attribute))+" "+str(type(getattr(model,attribute))))

    #generation des contraintes
    new_contraintes=[]
    for contrainte in model.constraints:
        #remplacement des sets
        contrainte=replaceStringOnSet(model,contrainte)
        
        #eclate la contrainte en contraintes atomiques
        li_contraintes=[]
        atomiseContrainte(contrainte,li_contraintes)

        #ajoute la liste de contraintes à la liste
        for cont in li_contraintes:
            if cont!=None: 
               if not None in cont : new_contraintes.append(cont)
            #new_contraintes.append(cont)
    
    for contr in new_contraintes:
        if(contr==None):continue
        #declaration des variables
        for i in range(1,len(contr)):
            contr[i]=str(contr[i]).replace("[","_")
            contr[i]=str(contr[i]).replace(",","_")
            contr[i]=str(contr[i]).replace("]","")
            
            #enregistrement des sets
            if(contr[i].__contains__('_to_')):
                numbers=contr[i].split('_to_')
                li=set(list(range(int(numbers[0]),int(numbers[1])+1)))
                name=[contr[i],li,True]
                if not name in new_variables: new_variables.append(name)

            #enregistrement des numériques
            elif(contr[i].isnumeric()):
                name=[contr[i],set(contr[i]),True]
                if not name in new_variables: new_variables.append(name)

            else:
                name=[contr[i],default_domain,False]
                if not name in new_variables: new_variables.append(name)

            #if(contr[i][0]=='_'):
            #    numbers=extractNumbers(contr[i])
            #    contr[i]=str(numbers[0])+'_to_'+str(numbers[-1])
        
    for contr in new_contraintes:
        print(str(contr))
    for variable in new_variables :
        print(variable)

    # result=[new_variables,new_contraintes]
    # return result

    #solutions = Launch_Solver(Ens, Cstr, False)
    solutions = Launch_Solver(new_variables, new_contraintes, True)

    WindowManager.display_solution(self, solutions)