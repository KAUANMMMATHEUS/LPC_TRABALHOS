class PhaseManager:
    def __init__(self):
        self.phase = 1
        self.next_phase_requested = False

    def get_phase(self):
        return self.phase

    def request_next_phase(self):
        self.next_phase_requested = True

    def advance_phase(self):
        self.phase += 1
        self.next_phase_requested = False
