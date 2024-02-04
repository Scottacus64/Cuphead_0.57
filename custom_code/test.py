from mpf.core.custom_code import CustomCode

INCREMENT_VALUE = 10
DELAY_SECS = 0.8

class DigitalReelDelay(CustomCode):

  def __init__(self, machine, name):
    super().__init__(machine, name)
    self._current_value = None

  def on_load(self):
    self.machine.events.add_handler('player_score', self._update_score)

  def _update_score(self, **kwargs):
    if self._current_value is None:
      self._current_value = kwargs.get('prev_value', 0)
      self._increment()

  def _increment(self):
    if self._current_value < self.machine.game.player['score']:
      self._current_value += INCREMENT_VALUE
      self.machine.events.post('player_score_reel',
                               value=self._current_value,
                               player_num=self.machine.game.player.number)
      self.machine.clock.schedule_once(self._increment, DELAY_SECS)
    else:
      self._current_value = None
