import parse, instanciation, solver
affichage=False
model=parse.MainApp().build(affichage)
instanciation.instanciate(model)