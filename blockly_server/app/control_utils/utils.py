from blockly_server.app.db_models.models import Projects
import os
import yaml
from blockly_server.extensions import process_manager,agent
from blockly_server.config import Config
import shutil
from flask import request
import time

MELODY_NAMES = [
    "click",
    "success",
    "error",
    "mario_coin",
    "mario_jump",
    "mario_start",
    "starwars_theme",
    "starwars_fanfare",
    "r2d2_chirp",
    "r2d2_talk",
    "r2d2_excited",
]

def get_all_projects():
    projects = Projects.query.all()
    projects_list = [pr.to_dict() for pr in projects]
    return projects_list

def stop_now():
    print('stop')
    if process_manager.get_process() is None:
        print("nothing running")
        return{'status': 'nothing running'}
    
    else:
        try:
            #process_manager.get_process().terminate()
            process_manager.get_process().kill()
            print("stopped")
            return {'status': 'stopped'}
        except Exception as e:
            print(e)
            return{'status': 'nothing running'}
        
def load_parameters():
    with open(Config.ADMIN_PARAMS, encoding=('utf-8')) as file:
        parameters = yaml.load(file, Loader=yaml.FullLoader)
    return parameters

def save_parameters(parameters):
    with open(Config.ADMIN_PARAMS, 'w', encoding=('utf-8')) as file:
        parameters = yaml.dump(parameters, file)

def get_robot_name():
    parameters = load_parameters()
    for key, value in parameters.items():
        if(key == "robot_name"):
            print("Getting robot name: ", value['value'] )
            return value['value']
    return " "

def get_sound_effects():
    """Return available buzzer melodies."""
    return MELODY_NAMES


def shutdown_flask():
    from win32api import GenerateConsoleCtrlEvent
    CTRL_C_EVENT = 0
    GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0)

def imed_exit():
    try:
       shutdown_flask()
    except Exception as e:
        os._exit(0)

def execute_blocks(code, stop_event=None):
    agent.execute(code)


def get_locale():
        lan = request.cookies.get('locale')
        if lan is not None:
            Config.LOCALE = lan
            return lan
        return request.accept_languages.best_match(['el', 'en'])

def initialize_app():
    """
    Function to initialize the application with necessary setups.
    """
    if not os.path.exists(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)
        os.makedirs(Config.PROJECT_DIR)
    elif not os.path.exists(Config.PROJECT_DIR):
        os.makedirs(Config.PROJECT_DIR)

    # Maintain an audio directory for compatibility with UI actions.
    sound_effects_dir = os.path.join(Config.DATA_DIR, 'sound_effects')
    os.makedirs(sound_effects_dir, exist_ok=True)

    #db.create_all()

    admin_params_path = Config.ADMIN_PARAMS
    if not os.path.exists(admin_params_path):
        shutil.copy(os.path.join(Config.APP_DIR, 'assets/code_templates/admin_parameters.yaml'), admin_params_path)
