from mpf.core.mode import Mode

class Base(Mode):

  def mode_init(self):
    self._current_value = None

  def mode_start(self, **kwargs):
      self.add_mode_event_handler('timer_mugReset_timer_complete', self.mugResetAgain)
      self.add_mode_event_handler('timer_cupReset_timer_complete', self.cupResetAgain)

  def mugResetAgain(self, **kwargs):
      if  self.machine.switch_controller.is_active(self.machine.switches['s_dt_M']) and self.machine.switch_controller.is_active(self.machine.switches['s_dt_U2']) and self.machine.switch_controller.is_active(self.machine.switches['s_dt_G']):
          self.machine.events.post('mugResetAgain')

  def cupResetAgain(self, **kwargs):
      if self.machine.switch_controller.is_active(self.machine.switches['s_dt_C']) and self.machine.switch_controller.is_active(self.machine.switches['s_dt_U']) and self.machine.switch_controller.is_active(self.machine.switches['s_dt_P']):
          self.machine.events.post('cupResetAgain')
