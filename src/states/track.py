from aiogram.fsm.state import StatesGroup, State


class TrackState(StatesGroup):
    entering_part_number = State()


class UntrackState(StatesGroup):
    entering_part_number = State()
