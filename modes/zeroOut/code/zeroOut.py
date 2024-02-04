from mpf.core.mode import Mode

# this is custom code that when called resets the score reels to 00000 for both players

class ZeroOut(Mode):

  def mode_init(self):
      """Initialize digital score reel."""
      self._frames = {}
      self._reel_count = 5
      self._include_player_number = False

  def mode_start(self, **kwargs):
      result = {'1': '2', '2': '2', '3': '2', '4': '2', '5': '2'}
      event_name = "score_reel_player_score_player1"
      self.machine.events.post(event_name, **result)
      event_name = "score_reel_player_score_player2"
      self.machine.events.post(event_name, **result)
      self.machine.events.post("rollOverClear")
