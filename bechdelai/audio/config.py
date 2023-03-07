from . import profiles


class Config:
    selected_profile: profiles.Profiles

    def select_profile(self, option):
        if option == "FR":
            self.selected_profile = profiles.French()

    def get_profile(self):
        return self.selected_profile
