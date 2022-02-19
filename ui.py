# os.environ['KIVY_GL_BACKEND']="sdl2"
import os
import pyautogui
import time
import asyncio
import threading
import model
import instanciation
from datetime import timedelta

from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
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

        # Chargement de l'écran de chargement
        self.loadingScreen = LoadingScreen.build(self)
        self.add_widget(self.loadingScreen)

        # Chargement de l'écran de sélection du modèle
        self.modelsScreen = ModelsScreen.build(self)
        self.add_widget(self.modelsScreen)
        self.current = "models_screen"

    def display_main_screen(self):
        self.current = "main_screen"

    def display_loading_screen(self):
        self.current = "loading_screen"

    def display_models_screen(self):
        self.current = "models_screen"

    def start_parsing(self, spinner, model_name):
        m = model.Model(model_name)

        self.ids.main_screen.add_widget(self.update_main_screen(m))
        
        self.display_main_screen()

    def search_solutions(self, m, button):
        self.ids.erreur_label.text = ""

        values = []
        for text_input in self.ids:
            if(text_input.endswith('_input')):
                if(self.ids[text_input].text == '' or int(self.ids[text_input].text) < 1):
                    return self.display_erreur("Erreur : Les valeurs saisies doivent toutes être supérieures ou égales à 1.")
                else:
                    values.append(self.ids[text_input].text)
        
        attributes = []
        for attribute in m.__dict__:
            if(attribute != 'resolution' and attribute != 'constraints' and getattr(m, attribute) == None):
                # print(str(attribute) + " : " + str(getattr(m,attribute)))
                attributes.append(str(attribute))

        for attribute in attributes:
            setattr(m, attribute, values[attributes.index(attribute)]) 

        instanciation.instanciate(m)

        # Afficher l'écran de chargement
        # self.display_loading_screen()

        # Lancer la résolution
        # x = threading.Thread(target=self.call_minizinc, args=[nb_golfeurs, nb_semaines, nb_groupes, taille_groupe])
        # x.start()

    # def call_minizinc(self, nb_golfeurs, nb_semaines, nb_groupes, taille_groupe):
    #     results = []

    #     try:
    #         # Load model from file
    #         m = Model("models/SGP_model2_optimized.mzn")

    #         # Find the MiniZinc solver configuration for Gecode
    #         gecode = Solver.lookup("gecode")

    #         # Create an Instance of the model for Gecode
    #         instance = Instance(gecode, m)

    #         # Assign values
    #         instance["nb_golfeurs"] = nb_golfeurs
    #         instance["nb_semaines"] = nb_semaines
    #         instance["nb_groupes"] = nb_groupes
    #         instance["taille_groupes"] = taille_groupe

    #         # Solve and print solution
    #         self.results = instance.solve(nr_solutions=1, timeout=timedelta(seconds=20))
    #         result = self.results.solution[0]
            
    #         self.ids.solution_label.text = str(result)
    #         self.ids.reinitialiser_button.disabled = False
    
    #         self.display_main_screen()

    #     except ValueError:
    #         pass

    def reinitialiser(self, button):
        for text_input in self.ids:
            if(text_input.endswith('_input')):
                self.ids[text_input].text = ""

        self.ids.solution_label.text = ""
        self.ids.erreur_label.text = ""
        self.ids.reinitialiser_button.disabled = True

    def display_erreur(self, erreur):
        self.ids.erreur_label.text = erreur

    def back(self, button):
        self.display_models_screen()

    def quit(self, button):
        App.get_running_app().stop()

    def update_main_screen(self, m):
        main_layout = FloatLayout()

        # BOUTON RETOUR
        button_back = Button(font_size="25px", text="Retour", size_hint=(0.1, 0.06), pos_hint={"x": 0.025, "top": 0.95}, background_normal='', background_color={1, .3, .4, .9})
        button_back.bind(on_release=self.back)
        main_layout.add_widget(button_back)

        # TITRE
        label_titre = Label(font_size="160px", font_name="fonts/Neonderthaw-Regular.ttf", text="Social Golfer", pos_hint={"center_x": 0.5, "top": 1}, size_hint=(1, 0.3))
        main_layout.add_widget(label_titre)

        content_layout = FloatLayout(size_hint=(1, 0.7))

        # PARTIE PARAMÈTRES
        settings_layout = FloatLayout(size_hint=(0.5, 1))

        label_parametres = Label(font_size="40px", text="Choix des paramètres :", size_hint=(1, 0.2), pos_hint={"center_x": 0.5, "top": 1})
        settings_layout.add_widget(label_parametres)

        attributes = []
        for attribute in m.__dict__:
            if(attribute != 'resolution' and attribute != 'constraints' and getattr(m, attribute) == None):
                attributes.append(str(attribute))

        for attribute in attributes:
            layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), pos_hint={"center_x": 0.5, "top": 0.8 - attributes.index(attribute) * (0.2 / (len(attributes) - 1))})
            layout.add_widget(Widget())
            label = Label(font_size="30px", text=attribute + " : ")
            layout.add_widget(label)
            text_input = TextInput(pos_hint={"center_y": 0.5}, size_hint=(None, None), size=(100, 30), multiline=False)
            layout.add_widget(text_input)
            layout.add_widget(Widget())
            settings_layout.add_widget(layout)
            self.ids[attribute + '_input'] = text_input

        erreur_label = Label(font_size="25px", color=(1, 0, 0, 1), bold=True, size_hint=(1, 0.1), pos_hint={"center_x": 0.5, "top": 0.5})
        settings_layout.add_widget(erreur_label)
        self.ids['erreur_label'] = erreur_label

        button_valider = Button(font_size="30px", text="Valider", size_hint=(0.25, 0.1), pos_hint={"center_x": 0.5, "y": 0.2}, background_normal='', background_color={1, .3, .4, .85})
        buttoncallback = partial(self.search_solutions, m)
        button_valider.bind(on_release=buttoncallback)
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

        return main_layout

class ModelsScreen(Screen):
    def build(self):
        width, height= pyautogui.size()

        screen = Screen(name="models_screen")

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

        # PARTIE CHOIX MODEL
        content_layout = FloatLayout(size_hint=(1, 0.7))

        label_models = Label(font_size="40px", text="Choisissez un modèle parmis la liste ci-dessous :", size_hint=(1, 0.2), pos_hint={"center_x": 0.5, "top": 0.9})
        content_layout.add_widget(label_models)

        models = []
        for file in os.listdir():
            if file.endswith(".xml"):
                models.append(file)

        spinner = Spinner(
            text='Choisir un modèle',
            font_size="25px",
            values=models,
            size_hint=(0.2, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        spinner.bind(text=self.start_parsing)
        content_layout.add_widget(spinner)

        button_quit = Button(font_size="30px", text="Quitter", size_hint=(0.15, 0.1), pos_hint={"right": 0.95, "y": 0.05}, background_normal='', background_color={1, .3, .4, .85})
        button_quit.bind(on_release=self.quit)
        content_layout.add_widget(button_quit)

        main_layout.add_widget(content_layout)
        window_layout.add_widget(main_layout)
        screen.add_widget(window_layout)

        return screen

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
        screen = Screen(name="main_screen")

        self.ids['main_screen'] = screen

        return screen        