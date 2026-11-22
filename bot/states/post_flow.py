from aiogram .fsm .state import State ,StatesGroup
class PostFlow (StatesGroup ):
    waiting_for_raw_text =State ()
    waiting_for_tone =State ()
    waiting_for_format =State ()
    ready_for_action =State ()