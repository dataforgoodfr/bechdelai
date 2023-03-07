from . import profiles


class Config:
    def __init__(self):
        self.selected_profile: profiles.Profiles

    def select_profile(self, option):
        if option == "FR":
            self.selected_profile = profiles.French()
        elif option == "US":
            self.selected_profile = profiles.USEnglish()

    def get_profile(self):
        return self.selected_profile
