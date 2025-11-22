from aiogram.fsm.state import StatesGroup, State



class Register(StatesGroup):
    full_name = State()
    phone_number = State()
    answer = State()
    every_one = State()
    
    
class QuestionState(StatesGroup):
    question_name = State()
    waiting_for_question = State()
    user_talk = State()
    user_id = State()
    user_answer = State()