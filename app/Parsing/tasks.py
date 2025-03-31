import os
import subprocess
from celery import shared_task

@shared_task
def run_games_list_parser():
    try:
        script_path = r"D:\VSC Projects\App\Project\app\Parsing\Games_list_bs4.py"
        python_exe = r"D:\VSC Projects\App\env\Scripts\python.exe"

        print("Скрипт должен быть запущен")
        result = subprocess.run([python_exe, script_path], capture_output=True, text=True)

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return str(e)
