import toga
from toga.constants import BOLD, COLUMN, ITALIC, MONOSPACE, NORMAL, ROW


class FontApp(toga.App):
    textpanel = None

    # Button callback functions
    def do_clear(self, widget, **kwargs):
        self.textpanel.value = ""

    def do_weight(self, widget, **kwargs):
        if widget.style.font_weight == NORMAL:
            widget.style.font_weight = BOLD
        else:
            widget.style.font_weight = NORMAL

    def do_style(self, widget, **kwargs):
        if widget.style.font_style == NORMAL:
            widget.style.font_style = ITALIC
        else:
            widget.style.font_style = NORMAL

    def do_monospace_button(self, widget, **kwargs):
        self.textpanel.value += widget.text + "\n"

    def do_icon_button(self, widget, **kwargs):
        self.textpanel.value += widget.id + "\n"

    def do_add_content(self, widget, **kwargs):
        new_lbl = toga.Label(
            "More Endor bold",
            font_family="Endor",
            font_size=14,
            font_weight=BOLD,
        )
        self.labels.add(new_lbl)

    def startup(self):
        # Set up main window
        self.main_window = toga.MainWindow()

        # register fonts
        toga.Font.register(
            "awesome-free-solid", "resources/Font Awesome 5 Free-Solid-900.otf"
        )
        toga.Font.register("Endor", "resources/ENDOR___.ttf")
        toga.Font.register("Endor", "resources/ENDOR___.ttf", weight=BOLD)
        toga.Font.register("Endor", "resources/ENDOR___.ttf", style=ITALIC)
        toga.Font.register("Endor", "resources/ENDOR___.ttf", weight=BOLD, style=ITALIC)
        toga.Font.register("Roboto", "resources/Roboto-Regular.ttf")
        toga.Font.register("Roboto", "resources/Roboto-Bold.ttf", weight=BOLD)
        toga.Font.register("Roboto", "resources/Roboto-Italic.ttf", style=ITALIC)
        toga.Font.register(
            "Roboto", "resources/Roboto-BoldItalic.ttf", weight=BOLD, style=ITALIC
        )

        button_style = {
            "font_family": "awesome-free-solid",
            "font_size": 14,
            "width": 50,
        }

        # Buttons
        btn_box1 = toga.Box(
            direction=ROW,
            margin_bottom=10,
            children=[
                toga.Button("Clear", on_press=self.do_clear),
                toga.Button("Weight", on_press=self.do_weight),
                toga.Button("Style", on_press=self.do_style),
                toga.Button("Add", on_press=self.do_add_content),
            ],
        )

        btn1 = toga.Button(
            "Monospace",
            on_press=self.do_monospace_button,
            font_family=MONOSPACE,
        )
        btn2 = toga.Button(
            "\uf0c5",
            id="copy",
            on_press=self.do_icon_button,
            **button_style,
        )
        btn3 = toga.Button(
            "\uf0ea",
            id="paste",
            on_press=self.do_icon_button,
            **button_style,
        )
        btn4 = toga.Button(
            "\uf0a9",
            id="arrow-right",
            on_press=self.do_icon_button,
            **button_style,
        )
        btn_box2 = toga.Box(
            direction=ROW,
            margin_bottom=10,
            children=[btn1, btn2, btn3, btn4],
        )

        # Labels
        lbl1 = toga.Label("Endor", font_family="Endor", font_size=14)
        lbl2 = toga.Label(
            "Endor bold",
            font_family="Endor",
            font_size=14,
            font_weight=BOLD,
        )
        lbl3 = toga.Label(
            "Endor italic",
            font_family="Endor",
            font_size=14,
            font_style=ITALIC,
        )
        lbl4 = toga.Label(
            "Endor bold italic",
            font_family="Endor",
            font_size=14,
            font_weight=BOLD,
            font_style=ITALIC,
        )
        lbl5 = toga.Label(
            "Roboto",
            font_family="Roboto",
            font_size=14,
        )
        lbl6 = toga.Label(
            "Roboto bold",
            font_family="Roboto",
            font_size=14,
            font_weight=BOLD,
        )
        lbl7 = toga.Label(
            "Roboto italic",
            font_family="Roboto",
            font_size=14,
            font_style=ITALIC,
        )
        lbl8 = toga.Label(
            "Roboto bold italic",
            font_family="Roboto",
            font_size=14,
            font_weight=BOLD,
            font_style=ITALIC,
        )

        unknown_style = {"font_family": "Unknown", "font_size": 14}
        lbl_u = toga.Label("Unknown", **unknown_style)
        lbl_ub = toga.Label("Unknown bold", font_weight=BOLD, **unknown_style)
        lbl_ui = toga.Label("Unknown italic", font_style=ITALIC, **unknown_style)
        lbl_ubi = toga.Label(
            "Unknown bold italic",
            font_weight=BOLD,
            font_style=ITALIC,
            **unknown_style,
        )

        self.textpanel = toga.MultilineTextInput(
            readonly=False, flex=1, placeholder="Ready."
        )

        self.labels = toga.Box(
            children=[
                lbl1,
                lbl2,
                lbl3,
                lbl4,
                lbl5,
                lbl6,
                lbl7,
                lbl8,
                lbl_u,
                lbl_ub,
                lbl_ui,
                lbl_ubi,
            ],
            direction=COLUMN,
        )
        # Outermost box
        outer_box = toga.Box(
            children=[
                btn_box1,
                btn_box2,
                self.labels,
                self.textpanel,
            ],
            flex=1,
            direction=COLUMN,
            margin=10,
        )

        # Add the content on the main window
        self.main_window.content = outer_box

        # Show the main window
        self.main_window.show()


def main():
    return FontApp("Font Example", "org.beeware.toga.examples.font")


if __name__ == "__main__":
    main().main_loop()
