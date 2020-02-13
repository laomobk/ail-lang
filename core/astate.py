from core import agc


class InterpreterState:
    def __init__(self):
        self.frame_stack :list = []
        self.gc : agc.GC = None

        self.err_stack = []
        self.global_interpreter = None  # global interpreter reference


MAIN_INTERPRETER_STATE = InterpreterState()