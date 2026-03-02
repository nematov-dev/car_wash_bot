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

# Admin stat

class ReportStates(StatesGroup):
    waiting_for_start = State()
    waiting_for_end = State()

class AdminStates(StatesGroup):
    adding_worker = State()
    deleting_worker = State()

    adding_admin_name = State()
    adding_admin_telegram = State()
    deleting_admin = State()

    adding_service_name = State()
    adding_service_price = State()
    deleting_service = State()

    waiting_for_broadcast_text = State()
