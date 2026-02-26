from aiogram.fsm.state import State, StatesGroup


# User add car state

class AddCarStates(StatesGroup):
    waiting_for_plate = State()