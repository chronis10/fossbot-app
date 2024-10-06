from blockly_server.app.db_models.models import Projects
import os
import yaml
import json
import glob
from blockly_server.extensions import process_manager,agent
from blockly_server.config import Config
import shutil
from flask import request
import time

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

def get_scenes():
    files = glob.glob(os.path.join(Config.DATA_DIR,'Coppelia_Scenes/*.ttt')) 
    names = [item.split("\\")[-1] for item in files]
    return names

def get_sound_effects():
    print("Getting sounds")    
    if os.path.exists(os.path.join(Config.DATA_DIR,'sound_effects')):
        mp3_sounds_list = glob.glob(os.path.join(Config.DATA_DIR,'sound_effects/*.mp3'))
        sounds_names = []
        for sound in mp3_sounds_list: 
            split_list = os.path.split(sound)
            audio_name = split_list[-1]
            audio_name_list = audio_name.split(".")
            audio_name = audio_name_list[0]
            sounds_names.append({ "sound_name": audio_name, "sound_path": os.path.normpath(sound)})        
        print("sound effects:")        
        #delete first the json file if exists and then create it again 
        if os.path.exists(os.path.join(Config.DATA_DIR,'sound_effects.json')):
            os.remove(os.path.join(Config.DATA_DIR,'sound_effects.json'))
        with open(os.path.join(Config.DATA_DIR,'sound_effects.json'), 'w') as out_file:
            json.dump(sounds_names, out_file)  


def shutdown_flask():
    from win32api import GenerateConsoleCtrlEvent
    CTRL_C_EVENT = 0
    GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0)

def imed_exit():
    try:
       shutdown_flask()
    except Exception as e:
        os._exit(0)

def execute_blocks(code):
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

    if Config.ROBOT_MODE == 'coppelia':
        coppelia_scenes_dir = os.path.join(Config.DATA_DIR, 'Coppelia_Scenes')
        if not os.path.exists(coppelia_scenes_dir):
            shutil.copytree(os.path.join(Config.APP_DIR, 'assets/coppelia_default'), coppelia_scenes_dir)


    sound_effects_dir = os.path.join(Config.DATA_DIR, 'sound_effects')
    if not os.path.exists(sound_effects_dir):
        shutil.copytree(os.path.join(Config.APP_DIR, 'assets/sound_effects'), sound_effects_dir)

    #db.create_all()
    get_sound_effects()

    admin_params_path = Config.ADMIN_PARAMS
    if not os.path.exists(admin_params_path):
        shutil.copy(os.path.join(Config.APP_DIR, 'assets/code_templates/admin_parameters.yaml'), admin_params_path)
