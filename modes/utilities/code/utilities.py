from pathlib import Path
import yaml

from mpf.core.mode import Mode


class Utilities(Mode):

    def mode_start(self, **kwargs):
        del kwargs

        self.machine.variables.set_machine_var("utilities_active", 1)
        self.machine.events.post("stop_attract")

        for light in self.machine.lights.values():
            light.remove_from_stack_by_key("show")
            light.remove_from_stack_by_key("mode")
            light.off(key="utility_reset")

        self.menu_items = [
            "LIGHT TEST",
            "SWITCH TEST",
            "COIL TEST",
            "AUDITS",
            "CLEAR AUDITS",
        ]
        self.menu_index = 0
        self.state = "menu"

        self.light_names = sorted(self.machine.lights.keys())
        self.light_index = 0

        self.coil_names = sorted([
            name for name in self.machine.coils.keys()
            if not name.endswith("_hold") and name != "c_play_meter"
        ])
        self.coil_index = 0
        self.coil_locked = False

        self.add_mode_event_handler("utility_left", self.left)
        self.add_mode_event_handler("utility_right", self.right)
        self.add_mode_event_handler("utility_select", self.select)
        self.add_mode_event_handler("exit_utilities", self.exit_utilities)

        self.machine.events.post("show_utility_topper")
        self.show_menu()

    def mode_stop(self, **kwargs):
        del kwargs
        self.machine.variables.set_machine_var("utilities_active", 0)
        self.all_lights_off()
        self.delay.remove("utility_light_cycle")
        self.delay.remove("utility_switch_refresh")
        self.delay.remove("utility_coil_unlock")
        self.machine.events.post("start_attract")

    def update_screen(self, title="", line1="", line2="", line3="", line4="", line5="", help_text=""):
        self.machine.events.post(
            "utility_update",
            utility_title=title,
            utility_line1=line1,
            utility_line2=line2,
            utility_line3=line3,
            utility_line4=line4,
            utility_line5=line5,
            utility_help=help_text,
        )

    def show_menu(self):
        self.state = "menu"
        self.delay.remove("utility_light_cycle")
        self.delay.remove("utility_switch_refresh")
        self.all_lights_off()

        selected = self.menu_items[self.menu_index]

        self.update_screen(
            title="UTILITIES",
            line1="Select Test Mode",
            line2="> " + selected,
            line3="",
            line4="",
            line5="",
            help_text="< / > = SCROLL    M = SELECT    X = EXIT",
        )

    def left(self, **kwargs):
        del kwargs

        if self.state == "menu":
            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
            self.show_menu()
        elif self.state == "coil":
            self.coil_index = (self.coil_index - 1) % len(self.coil_names)
            self.show_coil()
        elif self.state in ("switch", "light", "audits", "audit_clear_confirm"):
            self.show_menu()

        return True

    def right(self, **kwargs):
        del kwargs

        if self.state == "menu":
            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
            self.show_menu()
        elif self.state == "coil":
            self.coil_index = (self.coil_index + 1) % len(self.coil_names)
            self.show_coil()
        elif self.state in ("switch", "light", "audits", "audit_clear_confirm"):
            self.show_menu()

        return True

    def select(self, **kwargs):
        del kwargs

        if self.state == "menu":
            selected = self.menu_items[self.menu_index]

            if selected == "LIGHT TEST":
                self.start_light_test()
            elif selected == "SWITCH TEST":
                self.start_switch_test()
            elif selected == "COIL TEST":
                self.start_coil_test()
            elif selected == "AUDITS":
                self.start_audits_view()
            elif selected == "CLEAR AUDITS":
                self.confirm_clear_audits()

        elif self.state == "coil":
            self.fire_selected_coil()

        elif self.state == "audit_clear_confirm":
            self.clear_audits_file()

        return True

    def exit_utilities(self, **kwargs):
        del kwargs
        self.machine.variables.set_machine_var("utilities_active", 0)
        self.stop()
        return True

    # -------------------------
    # Light test
    # -------------------------

    def start_light_test(self):
        self.state = "light"
        self.light_index = 0

        self.update_screen(
            title="LIGHT TEST",
            line1="Cycling addressable LEDs",
            line2="One LED should be white at a time.",
            line3="",
            line4="",
            line5="",
            help_text="< OR > = BACK TO MENU    X = EXIT",
        )

        self.cycle_light()

    def all_lights_off(self):
        for light in self.machine.lights.values():
            light.remove_from_stack_by_key("show")
            light.remove_from_stack_by_key("mode")
            light.off(key="utility")
            light.off(key="utility_reset")

    def cycle_light(self):
        if self.state != "light":
            return

        if not self.light_names:
            self.update_screen(
                title="LIGHT TEST",
                line1="No lights found.",
                line2="",
                line3="",
                line4="",
                line5="",
                help_text="< OR > = BACK TO MENU    X = EXIT",
            )
            return

        self.all_lights_off()

        light_name = self.light_names[self.light_index]
        self.machine.lights[light_name].color("white", key="utility", priority=10000)

        self.update_screen(
            title="LIGHT TEST",
            line1=f"{self.light_index + 1} / {len(self.light_names)}",
            line2=light_name,
            line3="",
            line4="",
            line5="",
            help_text="< OR > = BACK TO MENU    X = EXIT",
        )

        self.light_index = (self.light_index + 1) % len(self.light_names)

        self.delay.add(
            ms=150,
            callback=self.cycle_light,
            name="utility_light_cycle"
        )

    # -------------------------
    # Switch test
    # -------------------------

    def start_switch_test(self):
        self.state = "switch"
        self.refresh_switch_test()

    def refresh_switch_test(self):
        if self.state != "switch":
            return

        active = []
        inactive_count = 0

        for name in sorted(self.machine.switches.keys()):
            switch = self.machine.switches[name]

            if self.machine.switch_controller.is_active(switch):
                active.append(name)
            else:
                inactive_count += 1

        if active:
            shown = active[:4]

            while len(shown) < 4:
                shown.append("")

            line1 = f"ACTIVE SWITCHES: {len(active)}"
            line2, line3, line4, line5 = shown
        else:
            line1 = "No switches active"
            line2 = f"Inactive switches: {inactive_count}"
            line3 = ""
            line4 = ""
            line5 = ""

        self.update_screen(
            title="SWITCH TEST",
            line1=line1,
            line2=line2,
            line3=line3,
            line4=line4,
            line5=line5,
            help_text="< OR > = BACK TO MENU    X = EXIT",
        )

        self.delay.add(
            ms=500,
            callback=self.refresh_switch_test,
            name="utility_switch_refresh"
        )

    # -------------------------
    # Coil test
    # -------------------------

    def start_coil_test(self):
        self.state = "coil"
        self.coil_index = 0
        self.show_coil()

    def show_coil(self):
        if not self.coil_names:
            self.update_screen(
                title="COIL TEST",
                line1="No coils found.",
                line2="",
                line3="",
                line4="",
                line5="",
                help_text="< OR > = BACK TO MENU    X = EXIT",
            )
            return

        coil_name = self.coil_names[self.coil_index]

        self.update_screen(
            title="COIL TEST",
            line1=f"{self.coil_index + 1} / {len(self.coil_names)}",
            line2=coil_name,
            line3="",
            line4="",
            line5="",
            help_text="< / > = SCROLL    M = FIRE COIL    X = EXIT",
        )

    def fire_selected_coil(self):
        if self.coil_locked or not self.coil_names:
            return

        coil_name = self.coil_names[self.coil_index]
        self.coil_locked = True

        try:
            self.machine.coils[coil_name].pulse()
            result = "FIRED"
        except Exception as e:
            result = f"ERROR: {e}"

        self.update_screen(
            title="COIL TEST",
            line1=f"{self.coil_index + 1} / {len(self.coil_names)}",
            line2=coil_name,
            line3=result,
            line4="",
            line5="",
            help_text="< / > = SCROLL    M = FIRE COIL    X = EXIT",
        )

        self.delay.add(
            ms=750,
            callback=self.unlock_coil,
            name="utility_coil_unlock"
        )

    def unlock_coil(self):
        self.coil_locked = False

        if self.state == "coil":
            self.show_coil()

    # -------------------------
    # Audits
    # -------------------------

    def audits_path(self):
        return Path(self.machine.machine_path) / "data" / "audits.yaml"

    def start_audits_view(self):
        self.state = "audits"
        path = self.audits_path()

        if not path.exists():
            self.update_screen(
                title="AUDITS",
                line1="audits.yaml not found",
                line2=str(path)[:40],
                line3="",
                line4="",
                line5="",
                help_text="< OR > = BACK TO MENU    X = EXIT",
            )
            return

        try:
            with path.open("r") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            self.update_screen(
                title="AUDITS",
                line1="ERROR READING FILE",
                line2=str(e)[:40],
                line3="",
                line4="",
                line5="",
                help_text="< OR > = BACK TO MENU    X = EXIT",
            )
            return

        events = data.get("events", {})
        game_started = events.get("game_started", 0)
        game_ended = events.get("game_ended", 0)

        self.update_screen(
            title="AUDITS",
            line1=f"Games Started: {game_started}",
            line2=f"Games Ended: {game_ended}",
            line3="",
            line4="",
            line5="",
            help_text="< OR > = BACK TO MENU    X = EXIT",
        )

    def confirm_clear_audits(self):
        self.state = "audit_clear_confirm"

        self.update_screen(
            title="CLEAR AUDITS?",
            line1="This will erase audits.yaml",
            line2="Press M to confirm",
            line3="Press < or > to cancel",
            line4="",
            line5="",
            help_text="M = ERASE    < OR > = CANCEL    X = EXIT",
        )

    def clear_audits_file(self):
        path = self.audits_path()

        try:
            with path.open("w") as f:
                f.write("{}\n")

            result = "audits.yaml erased"
        except Exception as e:
            result = f"ERROR: {e}"

        self.update_screen(
            title="AUDITS CLEARED",
            line1=result[:40],
            line2="",
            line3="",
            line4="",
            line5="",
            help_text="< OR > = BACK TO MENU    X = EXIT",
        )

        self.state = "audits"
