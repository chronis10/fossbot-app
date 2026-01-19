
import os
import json
import shutil
import requests
import subprocess
import signal
import sys
import threading
from flask import jsonify, send_file, request
from flask_socketio import emit
from blockly_server.app.db_models.models import Projects
from multiprocessing import Process
from blockly_server.extensions import db, process_manager
from blockly_server.config import Config
import time
from blockly_server.app.control_utils.utils import stop_now, execute_blocks, imed_exit, load_parameters, save_parameters, get_all_projects

if Config.ROBOT_MODE == "coppelia":
    from coppeliasim_zmqremoteapi_client import RemoteAPIClient

class SocketIOEvents:
    def __init__(self, socketio):
        self.socketio = socketio
        self.menu_process = None
        self.user_script_process = None
        self.user_script_running = threading.Event()
        self.start_menu_script()

    def find_python_executable(self):
        py_exec = shutil.which('python3')
        if py_exec is None:
            py_exec = shutil.which('python')
        if py_exec is None:
            py_exec = sys.executable
        return py_exec
    
    def kill_existing_oled_scripts(self):
        """
        Kills any previously running oled menu/screen scripts even if this server
        instance didn't start them (e.g. after restart/crash).
        """
        try:
            # graceful first
            subprocess.run(["pkill", "-f", r"oled_(menu|screen)\.py"], check=False)
            time.sleep(0.2)
            # hard kill if needed
            subprocess.run(["pkill", "-9", "-f", r"oled_(menu|screen)\.py"], check=False)
        except Exception as e:
            print("Could not pkill existing oled scripts:", e)

    def start_menu_script(self):
        # Always ensure no old oled scripts exist (handles restarts)
        self.kill_existing_oled_scripts()

        if self.menu_process is None or self.menu_process.poll() is not None:
            print("Starting menu script.")
            python_executable = self.find_python_executable()
            script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'scripts', 'oled_menu.py'
            )
            self.menu_process = subprocess.Popen(
                [python_executable, script_path],
                preexec_fn=os.setsid
            )

    def stop_menu_script(self):
        # Stop tracked process
        if self.menu_process and self.menu_process.poll() is None:
            print("Stopping menu script (tracked).")
            try:
                os.killpg(os.getpgid(self.menu_process.pid), signal.SIGTERM)
                self.menu_process.wait(timeout=2)
            except Exception:
                try:
                    os.killpg(os.getpgid(self.menu_process.pid), signal.SIGKILL)
                except Exception:
                    pass
            self.menu_process = None

        # Also stop any untracked leftovers
        self.kill_existing_oled_scripts()

    def register_events(self):
        self.socketio.on_event('connection', self.on_connect)
        self.socketio.on_event('disconnection', self.on_disconnect)
        self.socketio.on_error()(self.error_handler)
        self.socketio.on_event('get-all-projects', self.handle_get_all_projects)
        self.socketio.on_event('get_sound_effects', self.blockly_get_sound_effects)
        self.socketio.on_event('get_admin_panel_parameters', self.handle_get_admin_panel_parameters)
        self.socketio.on_event('save_parameters', self.handle_save_parameters)
        self.socketio.on_event('projects', self.handle_projects)
        self.socketio.on_event('new_project', self.handle_new_project)
        self.socketio.on_event('delete_project', self.handle_delete_project)
        self.socketio.on_event('edit_project', self.handle_edit_project)
        self.socketio.on_event('script_status', self.handle_script_status)
        self.socketio.on_event('stop_script', self.handle_stop_script)
        self.socketio.on_event('terminal_msgs', self.handle_terminal_msgs)
        self.socketio.on_event('fossbot_status', self.on_fossbot_status)
        self.socketio.on_event('execute_blockly', self.handle_execute_blockly)
        self.socketio.on_event('open_audio_folder', self.open_audio_folder)
        self.socketio.on_event('open_stage_folder', self.open_map_folder)
        self.socketio.on_event('open_map', self.open_map)
        self.socketio.on_event('reset_stage', self.reset_stage)
        self.socketio.on_event('send_xml', self.handle_send_xml)
        self.socketio.on_event('save_xml', self.handle_save_xml)
        self.socketio.on_event('systray_controls', self.handle_systray_controls)

    def on_connect(self, data):
        print("Socket connected, data received:", data)

    def on_disconnect(self, data):
        print("Socket disconnected!!, data received:", data)

    def error_handler(self, e):
        print('Error - socket IO : ', e)

    def handle_get_all_projects(self):
        projects_list = get_all_projects()
        emit('all-projects', {'status': '200', 'data': projects_list})

    def blockly_get_sound_effects(self):
        if os.path.exists(os.path.join(Config.DATA_DIR, 'sound_effects.json')):
            with open(os.path.join(Config.DATA_DIR, 'sound_effects.json'), 'r') as file:
                sounds = json.load(file)
                emit('sound_effects', {'status': 200, 'data': sounds})
        else:
            emit('sound_effects', {'status': 404, 'data': 'file does not exist'})

    def handle_get_admin_panel_parameters(self):
        parameters = load_parameters()
        parameters.pop('simulator_ids')
        emit('parameters', {'status': '200', 'parameters': parameters})

    def handle_save_parameters(self, data):
        try:
            params_values = json.loads(data['parameters'])
            parameters = load_parameters()
            for key, value in parameters.items():
                if key in ['robot_name', 'coppelia_path']:
                    value['value'] = params_values[key]
                elif key in ['coppelia_headless', 'rgb_led_type']:
                    value['value'] = params_values[key] == 'true'
                elif key != 'simulator_ids':
                    value['value'] = int(params_values[key])
            save_parameters(parameters)
            emit('save_parameters_result', {'status': '200', 'data': parameters})
        except Exception as e:
            print(e)
            emit('save_parameters_result', {'status': 'error', 'data': 'parameters not saved'})
    
    def handle_projects(self):
        projects_list = get_all_projects()
        data = jsonify(projects_list)
        emit('projects', { 'status': '200', 'data': data })

    def handle_new_project(self, data):
        title = data['title']
        info = data['info']
        project = Projects(title,info)
        db.session.add(project)
        db.session.commit()
        db.session.refresh(project)
        os.mkdir(os.path.join(Config.PROJECT_DIR,f'{project.project_id}'))
        shutil.copy(os.path.join(Config.APP_DIR,'assets/code_templates/template.xml'),os.path.join(Config.PROJECT_DIR,f'{project.project_id}/{project.project_id}.xml'))
        emit('new_project_result', { 'status': '200', 'project_id': project.project_id })

    def handle_delete_project(self, data):
        try:
            project_id = data['project_id']
            project = Projects.query.get(project_id)
            db.session.delete(project)
            db.session.commit()
            shutil.rmtree(os.path.join(Config.PROJECT_DIR,f'{project.project_id}'))
            emit('delete_project_result', {'status':'200', 'project_deleted': 'true' })
        except Exception as e:
            print(e)
            emit('delete_project_result', {'status':'error', 'project_deleted': 'false'})

    def handle_edit_project(self, project_id):
        try:
            project = Projects.query.get(project_id)
            project.title = request.args.get('title')    
            project.info = request.args.get('info')
            db.session.commit()       
            emit('edit_project', {'status':'updated'})
        except Exception as e:
            print(e)
            emit('edit_project', {'status':'error'})

    def handle_script_status(self):
        if self.user_script_process is None or not self.user_script_process.is_alive():
            emit('script_status', {'status': 'completed'})
        else:
            emit('script_status', {'status': 'still running'})

    def handle_stop_script(self):
        result = stop_now()
        self.user_script_running.clear()
        self.start_menu_script()
        emit('stop_script', result)

    def handle_terminal_msgs(self, data):
        self.socketio.emit('trm', data)

    def relay_to_robot(self, packet):
        self.socketio.emit('execute_fossbot', packet)
        self.socketio.emit('get_fossbot_status')

    def on_fossbot_status(self, data):
        print("FossBot status: ", data)
    
    def handle_execute_blockly(self, data):
        self.stop_menu_script()
        self.relay_to_robot(json.dumps(data))
        self.socketio.emit('execute_blockly_robot', {'status': '200', 'result': 'Code saved with success'})
        try:
            code = data['code']
            if Config.ROBOT_MODE == "coppelia":
                client = RemoteAPIClient()
                sim = client.require('sim')
                sim.startSimulation()
                time.sleep(1)
            
            if self.user_script_process and self.user_script_process.is_alive():
                stop_now()
                self.user_script_running.clear()
                time.sleep(0.5)

            self.user_script_running.set()
            self.user_script_process = Process(target=execute_blocks, args=(code,), daemon=True)
            self.user_script_process.start()
            process_manager.set_process(self.user_script_process)
            
            wait_thread = threading.Thread(target=self.wait_for_script_completion)
            wait_thread.start()

            emit('execute_blockly_result', {'status': '200'})
        except Exception as e:
            print(e)
            emit('execute_blockly_result', {'status': '400'})

    def wait_for_script_completion(self):
        if self.user_script_process:
            self.user_script_process.join()
        
        if self.user_script_running.is_set():
             self.user_script_running.clear()
             self.start_menu_script()

    def open_audio_folder(self):
        os.startfile(os.path.realpath(os.path.join(Config.DATA_DIR, 'sound_effects')))

    def open_map_folder(self):
        os.startfile(os.path.realpath(os.path.join(Config.DATA_DIR, 'Coppelia_Scenes')))

    def open_map(self, data):
        if Config.ROBOT_MODE == "coppelia" and '.ttt' in data:
            client = RemoteAPIClient()
            sim = client.require('sim')
            stop_now()
            self.user_script_running.clear()
            sim.stopSimulation()
            coppelia_dir = os.path.join(Config.DATA_DIR, 'Coppelia_Scenes')
            scene_name = os.path.join(coppelia_dir, data)
            sim.loadScene(scene_name)
            sim.startSimulation()

    def reset_stage(self):
        if Config.ROBOT_MODE == "coppelia":
            client = RemoteAPIClient()
            sim = client.require('sim')
            sim.stopSimulation()
            time.sleep(1)
            sim.startSimulation()

    def handle_send_xml(self, data):
        try:
            id = data['id']
            with open(os.path.join(Config.PROJECT_DIR, f'{id}/{id}.xml'), "r", encoding="utf8") as myfile:
                xml_data = myfile.readlines()
            emit('send_xml_result', {'status': '200', 'data': xml_data})
        except Exception as e:
            emit('send_xml_result', {'status': 'file not found'})

    def handle_save_xml(self, data):
        try:
            id = data['id']
            code = data['code']
            project = Projects.query.get(id)
            code = code.replace('</xml>', '')
            extra_info = ''.join(['  <project>\n', f'    <title>{project.title}</title>\n', f'    <description>{project.info}</description>\n', '  </project>\n', '</xml>'])
            code += extra_info
            with open(os.path.join(Config.PROJECT_DIR, f'{id}/{id}.xml'), "w", encoding="utf8") as fh:
                fh.write(code)
            emit('save_xml_result', {'status': '200', 'result': 'Code saved with success'})
        except Exception as e:
            emit('save_xml_result', {'status': 'error occured', 'result': 'Code was not saved'})

    def handle_systray_controls(self, message):
        if message['data'] == 'exit':
            self.stop_menu_script()
            imed_exit()
        else:
            print(message)

def register_socketio_events(socketio):
    events = SocketIOEvents(socketio)
    events.register_events()
