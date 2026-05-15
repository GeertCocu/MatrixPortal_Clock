import gc

class State(object):
    def __init__(self, state_id) -> None:
        self.state_id = state_id
        gc.collect()
        self.init_mem = gc.mem_free()

    def load(self):
        gc.collect()
        self.init_mem = gc.mem_free()

    def unload(self):
        self.logMem()
        gc.collect()

    def update(self):
        pass

    def logMem(self):
        gc.collect()
        mem_new = gc.mem_free()
        mem_diff = self.init_mem - mem_new
        self.init_mem = mem_new
        print("Memory used by {}: {} bytes, free: {}".format(self.state_id, mem_diff, mem_new))

