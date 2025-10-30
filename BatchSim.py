"""
时序模拟器：模拟任务的运行与调度。
"""
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import colorsys
import logging

# ========== 新增：日志系统配置 ==========
logging.basicConfig(
    level=logging.INFO,  # 默认不打印 DEBUG 信息
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BatchSim")

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
    def __init__(self, processes: list[Process], debug: bool = False):
        self.processes = processes
        self.time = 0

        self.ready_queue: List[Process] = []
        self.io_queue: List[Process] = []

        self.cpu_busy: Optional[Process] = None
        self.io_busy: Optional[Process] = None
        self.events = [] # (resource, pid, start_time, end_time)

        # ========== 新增：控制日志级别 ==========
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.debug = debug

    def initialize(self):
        # initialize processes
        for p in self.processes:
            p.start_next()
            self.ready_queue.append(p)

    """ Schedule processes to CPU and IO if available """
    def schedule_cpu(self):
        if self.cpu_busy is None and self.ready_queue:
            self.cpu_busy = self.ready_queue.pop(0)
            self.events.append(("CPU", self.cpu_busy.pid, "start", self.time))
            print(f"t={self.time}: CPU starts P{self.cpu_busy.pid}")

    def schedule_io(self):
        if self.io_busy is None and self.io_queue:
            self.io_busy = self.io_queue.pop(0)
            self.events.append(("IO", self.io_busy.pid, "start", self.time))
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
        self.events.append((resource_name, proc.pid, "end", self.time))
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

    def visualize(self):
        print("Visualizing Gantt Timeline...")
        logger.debug("Events:%s", self.events)

        pair_events = []
        temp = {}  # 暂存每个 (资源, pid) 的起始时间

        for res, pid, flag, t in self.events:
            key = (res, pid)
            if flag == "start":
                temp[key] = t
            elif flag == "end" and key in temp:
                pair_events.append((res, pid, temp[key], t))
                del temp[key]

        fig, ax = plt.subplots(figsize=(10, 4))

        y_map = {"CPU": 1, "IO": 0}

        logger.debug("Paired Events:%s", pair_events)
        # 为每个 pid 分配固定颜色
        pids = sorted(set(pid for _, pid, _, _ in pair_events))
        base_colors = plt.cm.tab10.colors  # 使用 matplotlib 内置配色
        pid_color_map = {pid: base_colors[i % len(base_colors)] for i, pid in enumerate(pids)}

        # 辅助函数：调整亮度
        def lighten_color(color, factor=0.4):
            """提高颜色亮度"""
            h, l, s = colorsys.rgb_to_hls(*color)
            l = min(1, l + factor * (1 - l))
            return colorsys.hls_to_rgb(h, l, s)

        y_map = {"CPU": 1, "IO": 0}

        for event in pair_events:
            if len(event) < 4:
                continue
            res, pid, start, end = event
            color = pid_color_map[pid]
            if res == "IO":
                color = lighten_color(color, 0.4)  # IO颜色更亮
            ax.barh(y_map[res], end - start, left=start, label=f"P{pid}",color=color, edgecolor="black")

            ax.text(start + (end - start) / 2, y_map[res],
                    f"P{pid}", ha='center', va='center', fontsize=8, color='black')

        ax.set_yticks([0, 1])
        ax.set_yticklabels(["IO", "CPU"])
        ax.set_xlabel("Time")
        ax.set_title("Gantt Timeline")
        ax.grid(True, axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()

tasks = [
    Process(pid=1, segments=[Segment("CPU", 5), Segment("IO", 4), Segment("CPU", 3)]),
    Process(pid=2, segments=[Segment("CPU", 3), Segment("IO", 2), Segment("CPU", 4)]),
    Process(pid=3, segments=[Segment("CPU", 4), Segment("IO", 7), Segment("CPU", 2)]),
]

sim = BatchSim(processes=tasks, debug=True)
sim.run()
sim.visualize()
