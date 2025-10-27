import threading
from task import automator
from data import button_data, box_data


def make_thread_task():
    enable_execute_button()
    task_thread = threading.Thread(target=automator.start_task, daemon=False)
    # task_thread = threading.Thread(target=test_rb_value(), daemon=False)
    task_thread.start()

# def test_rb_value():
#     print(box_data.BoxData().get_rb_value())

def enable_execute_button():
    buttons = button_data.ButtonData()
    buttons.set_all_buttons(False)
