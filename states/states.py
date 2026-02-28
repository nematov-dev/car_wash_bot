from aiogram.fsm.state import State, StatesGroup


# User add car state

class AddCarStates(StatesGroup):
    waiting_for_plate = State()


# Admin manual order state

class ManualOrderStates(StatesGroup):
    waiting_for_plate = State() 
    selecting_washer = State()    
    waiting_for_service = State() 
    waiting_for_price = State()  

# Admin confirm order state

class AudioOrderStates(StatesGroup):
    confirming = State()