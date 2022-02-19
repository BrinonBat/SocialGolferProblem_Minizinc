import instanciation, solver, ui
from kivy.app import App

class MainApp(App):
    def build(self):
        root = ui.WindowManager(transition=ui.NoTransition())
        root.build()
        return root

MainApp().run()
# instanciation.instanciate(model)