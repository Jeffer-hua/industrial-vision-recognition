import signal
import psutil


def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return "error"
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)
