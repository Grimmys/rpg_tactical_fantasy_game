class Skill:
    def __init__(self, name, formatted_name, desc):
        self.name = name
        self.formatted_name = formatted_name
        self.desc = desc

    def __eq__(self, o):
        return self.name == o
