import gc

class State(object):
    def __init__(self, stateId) -> None:
        self.stateId = stateId
        gc.collect()
        self.init_mem = gc.mem_free()

    def load(self):
        gc.collect()
        self.init_mem = gc.mem_free()

    def unload(self):
        self.logMem()

    def update(self):
        pass

    def logMem(self):
        gc.collect()
        mem_new = gc.mem_free()
        mem_diff = self.init_mem - mem_new
        self.init_mem = mem_new
        print("Memory used by {}: {} bytes, free: {}".format(self.stateId, mem_diff, mem_new))

