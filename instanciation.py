from sre_compile import isstring



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
                print(" this one is not numeric : "+str(attribute)+" : "+str(getattr(model,attribute)))
                return True
    return False

#tested
def replaceString(model,phrase):
    for attribute in model.__dict__:
        if(str((getattr(model,attribute))).isnumeric()):
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

    
    
    


#le modèle ici est déjà complet. Les variables ont été saisies au préalable par l'utilisateur à laide des méthodes suviantes:
def instanciate(model):
    #affichage du modèle
    for attribute in model.__dict__:
        if attribute !='resolution' and attribute!='constraints':
            print(str(attribute)+" : "+str(getattr(model,attribute))+" "+str(type(getattr(model,attribute))))
            if getattr(model,attribute)==None : setattr(model,attribute,'2')

    #maj valeurs variables
    calculateVariables(model)

    #maj des sets
    for attribute in model.__dict__:
        if attribute !='resolution' and attribute!='constraints':
            if isSet(model,attribute): #uniquement pour les sets
                new_one=replaceString(model,getattr(model,attribute))
                new_one=new_one.split('..')
                print(new_one)
                new_one=list(range(int(new_one[0]),int(new_one[1])+1))
                print(new_one)
                setattr(model,attribute,new_one)

    #generation des contraintes
    new_contraintes=[]
    for contrainte in model.constraints:
        #remplacement des sets

        #eclate la contrainte en contraintes atomiques

        #ajoute la liste de contraintes à la liste