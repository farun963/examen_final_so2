import time
from typing import List, Dict, Tuple
import json
from dataclasses import dataclass
import argparse


@dataclass
class Process:
    id: str
    arrival_time: int
    burst_time: int
    remaining_time: int = None

    def __post_init__(self):
        if self.remaining_time is None:
            self.remaining_time = self.burst_time


class ProcessScheduler:
    def __init__(self, processes: List[Process]):
        self.processes = processes
        self.current_time = 0
        self.execution_sequence = []
        self.completion_times = {}
        self.waiting_times = {}
        self.turnaround_times = {}

    def round_robin(self, quantum: int) -> Tuple[List[str], Dict]:
        remaining_processes = self.processes.copy()
        ready_queue = []
        self.current_time = 0
        self.execution_sequence = []

        for process in remaining_processes:
            process.remaining_time = process.burst_time

        while remaining_processes or ready_queue:
            new_arrivals = [p for p in remaining_processes if p.arrival_time <= self.current_time]
            ready_queue.extend(new_arrivals)
            for p in new_arrivals:
                remaining_processes.remove(p)

            if not ready_queue:
                self.current_time += 1
                continue

            current_process = ready_queue.pop(0)
            execution_time = min(quantum, current_process.remaining_time)

            self.execution_sequence.extend([current_process.id] * execution_time)
            self.current_time += execution_time
            current_process.remaining_time -= execution_time

            if current_process.remaining_time > 0:
                ready_queue.append(current_process)
            else:
                self.completion_times[current_process.id] = self.current_time
                self.calculate_metrics(current_process)

        return self.execution_sequence, self.get_metrics()

    def shortest_remaining_time_first(self) -> Tuple[List[str], Dict]:
        remaining_processes = self.processes.copy()
        self.current_time = 0
        self.execution_sequence = []

        for process in remaining_processes:
            process.remaining_time = process.burst_time

        while remaining_processes:
            eligible_processes = [p for p in remaining_processes if p.arrival_time <= self.current_time]

            if not eligible_processes:
                self.current_time += 1
                continue

            current_process = min(eligible_processes, key=lambda x: x.remaining_time)

            self.execution_sequence.append(current_process.id)
            self.current_time += 1
            current_process.remaining_time -= 1

            if current_process.remaining_time == 0:
                remaining_processes.remove(current_process)
                self.completion_times[current_process.id] = self.current_time
                self.calculate_metrics(current_process)

        return self.execution_sequence, self.get_metrics()

    def calculate_metrics(self, process: Process):
        completion_time = self.completion_times[process.id]
        turnaround_time = completion_time - process.arrival_time
        waiting_time = turnaround_time - process.burst_time

        self.turnaround_times[process.id] = turnaround_time
        self.waiting_times[process.id] = waiting_time

    def get_metrics(self) -> Dict:
        avg_waiting_time = sum(self.waiting_times.values()) / len(self.waiting_times)
        avg_turnaround_time = sum(self.turnaround_times.values()) / len(self.turnaround_times)

        return {
            "completion_times": self.completion_times,
            "waiting_times": self.waiting_times,
            "turnaround_times": self.turnaround_times,
            "average_waiting_time": avg_waiting_time,
            "average_turnaround_time": avg_turnaround_time
        }


def load_processes_from_file(filename: str) -> List[Process]:
    with open(filename, 'r') as f:
        data = json.load(f)
    return [Process(id=p['id'],
                    arrival_time=p['arrival_time'],
                    burst_time=p['burst_time'])
            for p in data]


def main():
    parser = argparse.ArgumentParser(description='Process Scheduler')
    parser.add_argument('--algorithm', type=str, required=True,
                        choices=['rr', 'srtf'],
                        help='Scheduling algorithm (rr: Round Robin, srtf: Shortest Remaining Time First)')
    parser.add_argument('--quantum', type=int, default=2,
                        help='Time quantum for Round Robin algorithm')
    parser.add_argument('--input', type=str, required=True,
                        help='Input JSON file with process information')

    args = parser.parse_args()

    processes = load_processes_from_file(args.input)
    scheduler = ProcessScheduler(processes)

    if args.algorithm == 'rr':
        sequence, metrics = scheduler.round_robin(args.quantum)
    else:
        sequence, metrics = scheduler.shortest_remaining_time_first()

    print(f"\nEjecución de procesos: {' '.join(sequence)}")
    print("\nMétricas:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")


if __name__ == "__main__":
    main()