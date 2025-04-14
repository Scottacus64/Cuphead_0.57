from mpf.core.mode import Mode

class DashChecker(Mode):

    def mode_init(self):
        self.machine.events.add_handler("standUp1_hit", self.check_dash_vars)
        self.machine.events.add_handler("standUp2_hit", self.check_dash_vars)
        self.machine.events.add_handler("standUp3_hit", self.check_dash_vars)

    def check_dash_vars(self, **kwargs):
        p = self.player 
        if p.dashSU1 == 1 and p.dashSU2 == 1 and p.dashSU3 == 1:
            self.machine.events.post('standUps_complete')
