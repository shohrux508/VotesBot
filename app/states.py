from aiogram.fsm.state import StatesGroup, State


class VotesStates(StatesGroup):
    get_category_title = State()
    get_candidate = State()
