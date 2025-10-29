"""
时序模拟器：模拟任务的运行与调度。
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class Segment:
    type: str  # "CPU" or "IO"
    duration: int

@dataclass
class Process:
    pid: int
    segments: List[Segment] = field(default_factory=list)
    current_index: int = 0  # 当前执行的段索引
    remaining: int = 0      # 当前段剩余时间

    """
        start next segment load time,
        return False if no more segments
    """
    def start_next(self):
        if self.current_index >= len(self.segments):
            return False
        seg = self.segments[self.current_index]
        self.remaining = seg.duration
        return True

    """
        execute current segment for time units,
    """
    def is_finished(self):
        return self.current_index >= len(self.segments)


class BatchSim:
    def __init__(self, processes: list[Process]):
        self.processes = processes
        self.time = 0

        self.ready_queue: List[Process] = []

        self.io_queue: List[Process] = []

        self.cpu_busy: Optional[Process] = None
        self.io_busy: Optional[Process] = None

    def initialize(self):
        # initialize processes
        for p in self.processes:
            p.start_next()
            self.ready_queue.append(p)

    """ Schedule processes to CPU and IO if available """
    def schedule_cpu(self):
        if self.cpu_busy is None and self.ready_queue:
            self.cpu_busy = self.ready_queue.pop(0)
            print(f"t={self.time}: CPU starts P{self.cpu_busy.pid}")

    def schedule_io(self):
        if self.io_busy is None and self.io_queue:
            self.io_busy = self.io_queue.pop(0)
            print(f"t={self.time}: IO starts P{self.io_busy.pid}")

    def handle_segment_complete(self, proc: Process):
        print(f"t={self.time}: P{proc.pid} {proc.segments[proc.current_index].type} segment done")
        proc.current_index += 1

        if proc.is_finished():
            print(f"t={self.time}: ✅ P{proc.pid} completed")
            return

        proc.start_next()
        next_type = proc.segments[proc.current_index].type
        (self.io_queue if next_type == "IO" else self.ready_queue).append(proc)


    def run_one_unit(self, proc: Process, resource_name: str):
        proc.remaining -= 1
        if proc.remaining > 0:
            return proc

        self.handle_segment_complete(proc)
        print(f"t={self.time}: {resource_name} released P{proc.pid}")
        return None  # 该资源空闲

    """ Simulate one time step """
    def simulate_step(self):

        if self.cpu_busy:
            self.cpu_busy = self.run_one_unit(self.cpu_busy, "CPU")

        if self.io_busy:
            self.io_busy = self.run_one_unit(self.io_busy, "IO")

        self.schedule_cpu()
        self.schedule_io()

        self.time += 1

    def run(self):
        print("Running Batch Simulation...\n")
        self.initialize()

        while (self.ready_queue or self.io_queue or
                self.cpu_busy or self.io_busy):
            self.simulate_step()

        print("\nSimulation Completed at t =", self.time)
tasks = [
    Process(pid=1, segments=[Segment("CPU", 5), Segment("IO", 4), Segment("CPU", 3)]),
    Process(pid=2, segments=[Segment("CPU", 3), Segment("IO", 2)]),
    Process(pid=3, segments=[Segment("CPU", 4)]),
]

sim = BatchSim(processes=tasks)
sim.run()
