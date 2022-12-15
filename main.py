import os
import sys
from Player import Player
import pygatt
import kivy
from binascii import hexlify
from horserace_helpers import *
from ObjectOrientedTest import *

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from odrive_helpers import digital_read
from threading import Thread
from time import sleep
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.clock import Clock

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

from odrive_helpers import *
import time

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

global vernier1
global vernier2
global vernier3
global vernier4

class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER

    print("class created")


Window.clearcolor = (1, 1, 1, 1)  # White

class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    count = 0
    elapsed = ObjectProperty()

    def beginning_setup(self):
        global homed
        if homed is False:
            assert od_1.config.enable_brake_resistor is True, "Check for faulty brake resistor."
            assert od_2.config.enable_brake_resistor is True, "Check for faulty brake resistor."

            horse1.set_gains()
            horse2.set_gains()
            horse3.set_gains()
            horse4.set_gains()

            # Checks the ODrive Calibraton
            if not horse1.is_calibrated():
                print("calibrating horse1...")
                horse1.calibrate_with_current_lim(15)
            if not horse2.is_calibrated():
                print("calibrating horse2...")
                horse2.calibrate_with_current_lim(15)
            if not horse3.is_calibrated():
                print("calibrating horse3...")
                horse3.calibrate_with_current_lim(15)
            if not horse4.is_calibrated():
                print("calibrating horse4...")
                horse4.calibrate_with_current_lim(15)

            # Homes the Horses to Left Side
            horses = [horse1, horse2, horse3, horse4]
            for horse in horses:
                horse.set_ramped_vel(1, 1)
            sleep(1)
            for horse in horses:
                horse.wait_for_motor_to_stop()  # waiting until motor slowly hits wall
            for horse in horses:
                horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
            sleep(3)  # allows motor to start moving to offset position
            for horse in horses:
                horse.wait_for_motor_to_stop()
            for horse in horses:
                horse.set_home()

            horse1.set_vel(0)
            horse2.set_vel(0)
            horse3.set_vel(0)
            horse4.set_vel(0)

            dump_errors(od_1)
            dump_errors(od_2)

            od_1.clear_errors()
            od_2.clear_errors()

            homed = True
            return homed

    def redraw(self, args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def check_all_sensors(self):
        return

    def thread_check_all_sensors(self):
        return

    def switch_to_traj(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = TRAJ_SCREEN_NAME

    def switch_to_gpio(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = GPIO_SCREEN_NAME

    def switch_to_beginning(self):
        SCREEN_MANAGER.transition.direction = "down"
        SCREEN_MANAGER.current = BEGINNING_SCREEN_NAME

    ##CONNECTED TO THE HOME BUTTON##

    def home_all_horses(self):
        horses = [horse1, horse2, horse3, horse4]
        for horse in horses:
            horse.set_ramped_vel(1, 1)
        sleep(1)
        for horse in horses:
            horse.wait_for_motor_to_stop()  # waiting until motor slowly hits wall
        for horse in horses:
            horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
        sleep(3)  # allows motor to start moving to offset position
        for horse in horses:
            horse.wait_for_motor_to_stop()
        for horse in horses:
            horse.set_home()

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'

    print("screen 1 created")

    def quit(self):
        print("Exit")
        quit()


class BeginningScreen(Screen):
    def switch_screen1(self):
        SCREEN_MANAGER.transition.direction = "down"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def move_to_baseline_screen(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

    def one_adapater_start(self):
        adapter1.start()
        print('adapter1 started')

    def two_adapter_start(self):
        adapter1.start()
        print('adapter1 started')
        adapter2.start()
        print('adapter2 started')

    def three_adapter_start(self):
        adapter1.start()
        print('adapter1 started')
        adapter2.start()
        print('adapter2 started')
        adapter3.start()
        print('adapter3 started')

    def four_adapter_start(self):
        adapter1.start()
        print('adapter1 started')
        adapter2.start()
        print('adapter2 started')
        adapter3.start()
        print('adapter3 started')
        adapter4.start()
        print('adapter4 started')

    def one_player(self):
        global numberOfPlayers

        self.one_adapater_start()
        self.move_to_baseline_screen()

        numberOfPlayers = 1
        return numberOfPlayers

    def two_players(self):
        global numberOfPlayers
        if numberOfPlayers == 2:
            self.move_to_baseline_screen()

        else:
            self.two_adapter_start()
            self.move_to_baseline_screen()

            numberOfPlayers = 2
            return numberOfPlayers

    def three_players(self):
        global numberOfPlayers
        if numberOfPlayers == 3:
            self.move_to_baseline_screen()

        elif numberOfPlayers == 2:
            adapter3.start()
            print('adapter3 started')

            self.move_to_baseline_screen()

            numberOfPlayers = 3
            return numberOfPlayers

        else:
            self.three_adapter_start()
            self.move_to_baseline_screen()

            numberOfPlayers = 3
            return numberOfPlayers

    def four_players(self):
        global numberOfPlayers
        if numberOfPlayers == 4:
            self.move_to_baseline_screen()

        elif numberOfPlayers == 3:
            adapter4.start()
            print('adapter4 started')

            self.move_to_baseline_screen()

            numberOfPlayers = 4
            return numberOfPlayers

        elif numberOfPlayers == 2:
            adapter3.start()
            print('adapter3 started')
            adapter4.start()
            print('adapter4 started')

            self.move_to_baseline_screen()

            numberOfPlayers = 4
            return numberOfPlayers

        else:
            self.four_adapter_start()
            self.move_to_baseline_screen()

            numberOfPlayers = 4
            return numberOfPlayers

    print("Beginning Screen Created")


class BaselineScreen(Screen):

    def find_baseline(self):
        global baseline1, baseline2, baseline3, baseline4, vernier1, vernier2, vernier3, vernier4, i
        if numberOfPlayers == 1:
            vernier1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier1 connected')

            while i < 4:
                vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(1))
                sleep(1)
                print('searching')
                i += 1

            baseline1 = round(average_heartrate(baseline1List))

            self.ids.player1Baseline.text = str(baseline1)

            sleep(5)

            SCREEN_MANAGER.transition.direction = "right"
            SCREEN_MANAGER.current = RUN_SCREEN_NAME

        if numberOfPlayers == 2:
            vernier1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier1 connected')
            vernier2 = adapter2.connect(player2.deviceID)
            print('vernier2 connected')

            while i < 4:
                vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(1))
                vernier2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(2))
                sleep(1)
                print('searching')
                i += 1

            baseline1 = round(average_heartrate(baseline1List))
            baseline2 = round(average_heartrate(baseline2List))

            self.ids.player1Baseline.text = str(baseline1)
            self.ids.player2Baseline.text = str(baseline2)
            self.ids.player3Baseline.text = "No Player!"
            self.ids.player4Baseline.text = "No Player!"

            sleep(5)

            SCREEN_MANAGER.transition.direction = "right"
            SCREEN_MANAGER.current = RUN_SCREEN_NAME

        elif numberOfPlayers == 3:
            i = 0
            vernier1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier1 connected')
            vernier2 = adapter2.connect(player2.deviceID)
            print('vernier2 connected')
            vernier3 = adapter3.connect(player3.deviceID)
            print('vernier3 connected')

            while i < 4:
                vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(1))
                vernier2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(2))
                vernier3.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(3))
                sleep(1)
                print(baseline3List)
                i += 1

            baseline1 = round(average_heartrate(baseline1List))
            baseline2 = round(average_heartrate(baseline2List))
            baseline3 = round(average_heartrate(baseline3List))

            self.ids.player1Baseline.text = str(baseline1)
            self.ids.player2Baseline.text = str(baseline2)
            self.ids.player3Baseline.text = str(baseline3)
            self.ids.player3Baseline.text = "No Player!"

            sleep(5)

            SCREEN_MANAGER.transition.direction = "right"
            SCREEN_MANAGER.current = RUN_SCREEN_NAME

        elif numberOfPlayers == 4:  # WIP
            vernier1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier1 connected')
            vernier2 = adapter2.connect(player2.deviceID)
            print('vernier2 connected')
            vernier3 = adapter3.connect(player3.deviceID)
            print('vernier3 connected')
            vernier4 = adapter4.connect(player4.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier4 connected')

            vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(1))
            vernier2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(2))
            vernier3.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(3))
            vernier4.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(4))

            adapter1.stop()
            adapter2.stop()
            adapter3.stop()
            adapter4.stop()

        else:
            print('not working L')
            return

        return baseline1, baseline2, baseline3, baseline4, vernier1, vernier2, i

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = BEGINNING_SCREEN_NAME

    print("Baseline Screen Created")


class RunScreen(Screen):
    def update_baseline(self):
        self.ids.player1Baseline.text = str(baseline1)
        self.ids.player2Baseline.text = str(baseline2)
        self.ids.player3Baseline.text = str(baseline3)
        self.ids.player4Baseline.text = str(baseline4)

    def start_game(self):
        global new_game
        t = "5"
        while int(t) > 0:
            t = str(int(t) - 1)
            sleep(1)
        self.ids.count.text = "GO!"
        sleep(.5)
        if numberOfPlayers == 1:
            try:
                vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(1))

                player1.start_game()

                while new_game is False:
                    time.sleep(2)
                    print("while True is running")

                print('new game')
                horse1.set_vel(0)
                horse2.set_vel(0)
                horse3.set_vel(0)
                horse4.set_vel(0)
                SCREEN_MANAGER.transition.direction = "right"
                SCREEN_MANAGER.current = MAIN_SCREEN_NAME
                new_game = False
                return new_game

            finally:
                print('quit?')

        elif numberOfPlayers == 2:
            try:
                vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(1))
                vernier2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(2))

                player1.start_game()
                player2.start_game()

                while new_game is False:
                    time.sleep(2)
                    print("while True is running")

                print('new game')
                horse1.set_vel(0)
                horse2.set_vel(0)
                horse3.set_vel(0)
                horse4.set_vel(0)
                SCREEN_MANAGER.transition.direction = "right"
                SCREEN_MANAGER.current = MAIN_SCREEN_NAME
                new_game = False
                return new_game

            finally:
                print('quit?')


class TrajectoryScreen(Screen):
    """
    Class to handle the trajectory control screen and its associated touch events
    """

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def submit_trapezoidal_traj(self):
        horse1.set_vel_limit(10)
        horse2.set_vel_limit(10)
        horse3.set_vel_limit(10)
        horse4.set_vel_limit(10)
        horse1.set_pos_traj(int(self.target_position.text), int(self.acceleration.text), int(self.target_speed.text),
                            int(self.deceleration.text))  # position 5, acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2
        horse2.set_pos_traj(int(self.target_position.text), int(self.acceleration.text), int(self.target_speed.text),
                            int(self.deceleration.text))  # position 5, acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2
        horse3.set_pos_traj(int(self.target_position.text), int(self.acceleration.text), int(self.target_speed.text),
                            int(self.deceleration.text))  # position 5, acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2
        horse4.set_pos_traj(int(self.target_position.text), int(self.acceleration.text), int(self.target_speed.text),
                            int(self.deceleration.text))  # position 5, acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2


class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

        print("admin screen created")

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()

    print("static methods created")


"""
Widget additions
"""

Builder.load_file('main.kv')
Builder.load_file('BeginningScreen.kv')
Builder.load_file('BaselineScreen.kv')
Builder.load_file('RunScreen.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(TrajectoryScreen(name=TRAJ_SCREEN_NAME))
SCREEN_MANAGER.add_widget(BeginningScreen(name=BEGINNING_SCREEN_NAME))
SCREEN_MANAGER.add_widget(BaselineScreen(name=BASELINE_SCREEN_NAME))
SCREEN_MANAGER.add_widget(RunScreen(name=RUN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))
print("various screens created")

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()
    print("mix panel")


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    print("done setting up")
    ProjectNameGUI().run()
