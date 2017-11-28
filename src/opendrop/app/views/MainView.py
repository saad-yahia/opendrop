from gi.repository import Gtk

from opendrop.app.bases.GtkApplicationWindowView import GtkApplicationWindowView
from opendrop.app.presenters.IMainView import IMainView


class MainView(GtkApplicationWindowView, IMainView):
    def setup(self) -> None:
        grid = Gtk.Grid(
            margin=10,
            column_spacing=10,
            row_spacing=10
        )

        self.window.add(grid)

        button1 = Gtk.Button(label='Timer example')
        button2 = Gtk.Button(label='Burger example')
        button3 = Gtk.Button(label='About')

        button1.event_name = 'on_timer_button_clicked'
        button2.event_name = 'on_burger_button_clicked'
        button3.event_name = 'on_about_button_clicked'

        grid.attach(button1, 0, 0, 1, 1)
        grid.attach(button2, 1, 0, 1, 1)
        grid.attach(button3, 0, 1, 2, 1)

        # About dialog
        self.about_dialog = Gtk.AboutDialog(
            program_name='Sample Application',
            version='1.0.0',
            website='http://www.example.org',
            comments='Example application with sample code to demonstrate use.',
            authors=['John', 'Jane', 'Jackson', 'Jennifer'],
            documenters=['Wayne'],
            transient_for=self.window,
            modal=True
        )

        self.window.show_all()

        for button in (button1, button2, button3):
            button.connect('clicked', self.on_buttonx_clicked)

    def on_buttonx_clicked(self, button: Gtk.Button) -> None:
        self.fire(button.event_name)

    def show_about_dialog(self) -> None:
        response = self.about_dialog.run()

        if response == Gtk.ResponseType.DELETE_EVENT or response == Gtk.ResponseType.CANCEL:
            self.about_dialog.hide()