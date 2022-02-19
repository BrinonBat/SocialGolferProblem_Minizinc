import ui
import xml.etree.ElementTree as ET
from kivy.app import App

class Model():
    def __init__(self, file):
        self.importXML(file)

    def importXML(self, file):
        tree = ET.parse(file)
        root = tree.getroot()

        setattr(self, 'resolution', root.get('resolution'))

        variables = root.find('variables')
        constraints = root.find('constraints')

        for variable in variables:
            tag = variable.tag
            if(tag == 'int'):
                if(variable.get("saisie") == "True"):
                    setattr(self, variable.get("id"), variable.text)
                else:
                    setattr(self, variable.get("id"), None)
            elif(tag == 'set'):
                setattr(self, variable.get("id"), variable.text)
            else:
                setattr(self, variable.get("id"), [])

        liste_constraints = []
        for constraint in constraints:
            result = self.get_constraint(constraint)

            liste_constraints.append(result)
            print(result)

        setattr(self, 'constraints', liste_constraints)

    def get_constraint(self, constraint):
        constraint_array = [constraint.tag]
        elemof = []
        actions = []

        childs = constraint.getchildren()
        for child in childs:
            if(child.tag == 'elemof'):
                string = child.get('name') + ' elemof ' + child.text
                elemof.append(string)
            else:
                result = self.get_childs(child)
                actions.append(result)

        constraint_array.append(elemof)
        constraint_array.append(actions)

        return constraint_array

    def get_childs(self, element):
        tag = element.tag
        if(tag == 'elem'):
            return element.text
        elif(tag == 'elemof'):
            return element.get('name') + ' elemof ' + element.text
        elif(tag == 'forall' or tag == 'condition' or tag == 'array_union'):
            return self.get_constraint(element)
        else:
            action = [element.tag]

            childs = element.getchildren()
            for child in childs:
                result = self.get_childs(child)
                action.append(result)

            return action    