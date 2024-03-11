import re

class QSSFileHelper:
    def __init__(self, path):
        self.load_qss_file(path)

    def load_qss_file(self, path):
        try:
            with open(path, 'r') as style_file:
                self.style_sheet = style_file.read()
        except FileNotFoundError:
            print("Error: Style file not found.")
            self.style_sheet = ""

    def extract_style_properties(self, selector):
        selector_copy = selector.replace(".", "\\.").replace("#", "\\#")
        combined_pattern = f"{selector_copy}\\s*{{([^\\}}]*)}}"
        regex = re.compile(combined_pattern, re.DOTALL)

        match = regex.search(self.style_sheet)

        if match:
            properties = match.group(1).strip()
            return properties
        else:
            return None
