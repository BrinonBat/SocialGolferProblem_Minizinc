# os.environ['KIVY_GL_BACKEND']="sdl2"
import os
import pyautogui
import time
import asyncio
import threading
import xml.etree.ElementTree as ET

from datetime import timedelta

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image

from minizinc import Instance, Model, Solver


class WindowManager(ScreenManager):
    def build(self):
        width, height= pyautogui.size()
        Window.size = (width, height)

        # Chargement de l'écran principal
        self.mainScreen = MainScreen.build(self)
        self.add_widget(self.mainScreen)
        self.current = "main_screen"

        # Chargement de l'écran de chargement
        loadingScreen = LoadingScreen.build(self)
        self.add_widget(loadingScreen)

    def display_main_screen(self):
        self.current = "main_screen"

    def display_loading_screen(self):
        self.current = "loading_screen"

    def search_solutions(self, button):
        self.ids.erreur_label.text = ""
        
        nbr_golfeurs = -1
        nbr_semaines = -1
        nbr_groupes = -1

        if(self.ids.nbr_golfeurs_input.text != ''): nbr_golfeurs = int(self.ids.nbr_golfeurs_input.text)
        if(self.ids.nbr_semaines_input.text != ''): nbr_semaines = int(self.ids.nbr_semaines_input.text)
        if(self.ids.nbr_groupes_input.text != ''): nbr_groupes = int(self.ids.nbr_groupes_input.text)

        if(nbr_golfeurs < 1 or nbr_semaines < 1 or nbr_groupes < 1):
            self.display_erreur("Erreur : Les valeurs saisies doivent être supérieures ou égales à 1.")
        elif(nbr_golfeurs % nbr_groupes != 0):
            self.display_erreur("Erreur : Le nombre de golfeurs n'est pas divisible par le nombre de groupes.")
        else:
            taille_groupes = int(nbr_golfeurs / nbr_groupes)

            self.display_loading_screen()

            x = threading.Thread(target=self.call_minizinc, args=[nbr_golfeurs, nbr_semaines, nbr_groupes, taille_groupes])
            x.start()

    def call_minizinc(self, nbr_golfeurs, nbr_semaines, nbr_groupes, taille_groupes):
        results = []

        try:
            # Load model from file
            model = Model("SGP_model1_optimized.mzn")

            # Find the MiniZinc solver configuration for Gecode
            gecode = Solver.lookup("gecode")

            # Create an Instance of the model for Gecode
            instance = Instance(gecode, model)

            # Assign values
            instance["nb_golfeurs"] = nbr_golfeurs
            instance["nb_semaines"] = nbr_semaines
            instance["nb_groupes"] = nbr_groupes
            instance["taille_groupe"] = taille_groupes

            # Solve and print solution
            self.results = instance.solve(nr_solutions=1, timeout=timedelta(seconds=20))
            result = self.results.solution[0]
            
            self.ids.solution_label.text = str(result)
            self.ids.reinitialiser_button.disabled = False
    
            self.display_main_screen()

        except ValueError:
            pass

    def reinitialiser(self, button):
        self.ids.solution_label.text = ""
        self.ids.nbr_golfeurs_input.text = ""
        self.ids.nbr_semaines_input.text = ""
        self.ids.nbr_groupes_input.text = ""
        self.ids.reinitialiser_button.disabled = True
        self.ids.erreur_label.text = ""

    def display_erreur(self, erreur):
        self.ids.erreur_label.text = erreur

    def quit(self, button):
        App.get_running_app().stop()

class LoadingScreen(Screen):
    def build(self):
        screen = Screen(name="loading_screen")

        main_layout = AnchorLayout(anchor_x='center', anchor_y='center')

        gif = Image(source="images/loading_animation.zip", anim_delay="0.5")
        main_layout.add_widget(gif)

        screen.add_widget(main_layout)

        return screen

class MainScreen(Screen):
    def build(self):
        width, height= pyautogui.size()

        screen = Screen(name="main_screen")

        window_layout = AnchorLayout(anchor_x='left', anchor_y='top')
        self.main_background = Widget()
        with self.canvas:
            Rectangle(size=(width, height), source='images/background.jpg')
            Color(0, 0, 0, 0.4)
            Rectangle(size=(width, height))
        window_layout.add_widget(self.main_background)

        main_layout = FloatLayout()

        # TITRE
        label_titre = Label(font_size="160px", font_name="fonts/Neonderthaw-Regular.ttf", text="Social Golfer", pos_hint={"center_x": 0.5, "top": 1}, size_hint=(1, 0.3))
        main_layout.add_widget(label_titre)

        content_layout = FloatLayout(size_hint=(1, 0.7))

        # PARTIE PARAMÈTRES
        settings_layout = FloatLayout(size_hint=(0.5, 1))

        label_parametres = Label(font_size="40px", text="Choix des paramètres :", size_hint=(1, 0.2), pos_hint={"center_x": 0.5, "top": 1})
        settings_layout.add_widget(label_parametres)

        nbr_golfeurs_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), pos_hint={"center_x": 0.5, "top": 0.8})
        nbr_golfeurs_layout.add_widget(Widget())
        label_nbr_golfeurs = Label(font_size="30px", text="Nbr de golfeurs : ")
        nbr_golfeurs_layout.add_widget(label_nbr_golfeurs)
        nbr_golfeurs_input = TextInput(pos_hint={"center_y": 0.5}, size_hint=(None, None), size=(100, 30), multiline=False)
        nbr_golfeurs_layout.add_widget(nbr_golfeurs_input)
        nbr_golfeurs_layout.add_widget(Widget())
        settings_layout.add_widget(nbr_golfeurs_layout)
        self.ids['nbr_golfeurs_input'] = nbr_golfeurs_input

        nbr_semaines_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), pos_hint={"center_x": 0.5, "top": 0.7})
        nbr_semaines_layout.add_widget(Widget())
        label_nbr_semaines = Label(font_size="30px", text="Nbr de semaines : ")
        nbr_semaines_layout.add_widget(label_nbr_semaines)
        nbr_semaines_input = TextInput(pos_hint={"center_y": 0.5}, size_hint=(None, None), size=(100, 30), multiline=False)
        nbr_semaines_layout.add_widget(nbr_semaines_input)
        nbr_semaines_layout.add_widget(Widget())
        settings_layout.add_widget(nbr_semaines_layout)
        self.ids['nbr_semaines_input'] = nbr_semaines_input

        nbr_groupes_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), pos_hint={"center_x": 0.5, "top": 0.6})
        nbr_groupes_layout.add_widget(Widget())
        label_nbr_groupes = Label(font_size="30px", text="Nbr de groupes : ")
        nbr_groupes_layout.add_widget(label_nbr_groupes)
        nbr_groupes_input = TextInput(pos_hint={"center_y": 0.5}, size_hint=(None, None), size=(100, 30), multiline=False)
        nbr_groupes_layout.add_widget(nbr_groupes_input)
        nbr_groupes_layout.add_widget(Widget())
        settings_layout.add_widget(nbr_groupes_layout)
        self.ids['nbr_groupes_input'] = nbr_groupes_input

        erreur_label = Label(font_size="25px", color=(1, 0, 0, 1), bold=True, size_hint=(1, 0.1), pos_hint={"center_x": 0.5, "top": 0.5})
        settings_layout.add_widget(erreur_label)
        self.ids['erreur_label'] = erreur_label

        button_valider = Button(font_size="30px", text="Valider", size_hint=(0.25, 0.1), pos_hint={"center_x": 0.5, "y": 0.2}, background_normal='', background_color={1, .3, .4, .85})
        button_valider.bind(on_release=self.search_solutions)
        settings_layout.add_widget(button_valider)

        content_layout.add_widget(settings_layout)

        # PARTIE RÉSULTATS
        results_layout = FloatLayout(size_hint=(0.5, 1), pos_hint={"x": 0.5})

        label_resultats = Label(font_size="40px", text="Résultats :", size_hint=(1, 0.2), pos_hint={"center_x": 0.5, "top": 1})
        results_layout.add_widget(label_resultats)

        label_solution = Label(font_size="30px", text="", size_hint=(1, 0.6), pos_hint={"center_x": 0.5, "top": 1})
        results_layout.add_widget(label_solution)
        self.ids['solution_label'] = label_solution

        button_reinitialiser = Button(font_size="30px", text="Réinitialiser", size_hint=(0.25, 0.1), pos_hint={"center_x": 0.5, "y": 0.2}, background_normal='', background_color={1, .3, .4, .85})
        button_reinitialiser.bind(on_release=self.reinitialiser)
        button_reinitialiser.disabled = True
        results_layout.add_widget(button_reinitialiser)
        self.ids['reinitialiser_button'] = button_reinitialiser

        button_quit = Button(font_size="30px", text="Quitter", size_hint=(0.25, 0.1), pos_hint={"right": 0.95, "y": 0.05}, background_normal='', background_color={1, .3, .4, .85})
        button_quit.bind(on_release=self.quit)
        results_layout.add_widget(button_quit)

        content_layout.add_widget(results_layout)

        main_layout.add_widget(content_layout)
        window_layout.add_widget(main_layout)

        screen.add_widget(window_layout)

        return screen

class Model():
    def __init__(self):
        print('init model')

class MainApp(App):
    def build(self):
        model = self.importXML('SGP_model2 _optimized.xml')
        root = WindowManager(transition=NoTransition())
        root.build()
        return root

    def importXML(self, file):
        tree = ET.parse(file)
        root = tree.getroot()

        model = Model()

        setattr(model, 'resolution', root.get('resolution'))

        variables = root.find('variables')
        constraints = root.find('constraints')

        for variable in variables:
            tag = variable.tag
            if(tag == 'int'):
                if(variable.get("saisie") == "True"):
                    setattr(model, variable.get("id"), variable.text)
                else:
                    setattr(model, variable.get("id"), None)
            elif(tag == 'set'):
                setattr(model, variable.get("id"), variable.text)
            else:
                setattr(model, variable.get("id"), [])

        liste_constraints = []
        for constraint in constraints:
            result = self.get_constraint(constraint)

            liste_constraints.append(result)
            print(result)

        setattr(model, 'constraints', liste_constraints)

        return model

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

MainApp().run()