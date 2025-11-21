from aiogram.fsm.state import StatesGroup, State



class Register(StatesGroup):
    full_name = State()
    answer = State()
    
    
class QuestionState(StatesGroup):
    question_name = State()
    waiting_for_question = State()