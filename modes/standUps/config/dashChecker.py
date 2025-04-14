from mpf.core.mode import GameMode

class DashChecker(Mode):

    def mode_init(self):
        self.add_player_event_handler("dashSU1", self.check_dash_vars)
        self.add_player_event_handler("dashSU2", self.check_dash_vars)
        self.add_player_event_handler("dashSU3", self.check_dash_vars)

    def chech_dash_vars(self, **kwargs):
        p = self.player 
        if p.dashSU1 == 1 and p.dashSU2 == 1 and p.dashSU3 == 1:
            self.machine.events.post(standUps_complete)