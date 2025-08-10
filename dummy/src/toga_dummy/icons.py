from .utils import LoggedObject


class Icon(LoggedObject):
    ICON_FAILURE = None
    EXTENSIONS = [".png", ".ico"]
    SIZES = None

    def __init__(self, interface, path):
        super().__init__()
        self.interface = interface
        if self.ICON_FAILURE:
            raise self.ICON_FAILURE
        else:
            match path:
                case None:
                    self.path = "<APP ICON>"
                case dict() if not path:
                    raise FileNotFoundError("No image variants found")
                case _:
                    self.path = path
