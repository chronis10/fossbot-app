import os
import json
import shutil
import requests
from flask import jsonify, send_file, request
from flask_socketio import emit
from app.db_models.models import Projects
from multiprocessing import Process
from extensions import db, process_manager
from config import Config
from app.control_utils.utils import stop_now, execute_blocks, imed_exit, load_parameters, save_parameters, get_all_projects, stop_now

def register_socketio_events(socketio):
    @socketio.on('connection')
    def on_connect(data):
        print("Socket connected, data received:", data)

    @socketio.on('disconnection')
    def on_disconnect(data):
        print("Socket disconnected!!, data received:", data)

    @socketio.on_error()  
    def error_handler(e):
        print('Error - socket  IO : ', e)

    @socketio.on('get-all-projects')
    def handle_get_all_projects():
        projects_list = get_all_projects()
        print('getting all projects')
        print(projects_list)

        emit('all-projects', { 'status': '200', 'data': projects_list})

    @socketio.on('get_sound_effects')
    def blockly_get_sound_effects():
        if os.path.exists(os.path.join(Config.DATA_DIR,'sound_effects.json')):
            with open(os.path.join(Config.DATA_DIR,'sound_effects.json'), 'r') as file:
                sounds = json.load(file)
                emit('sound_effects',  { 'status': 200, 'data': sounds })
        else:
            emit('sound_effects', { 'status': 404, 'data': 'file does not exist'})       

    @socketio.on('get_admin_panel_parameters')
    def handle_get_admin_panel_parameters():
        parameters = load_parameters()
        parameters.pop('simulator_ids')
        emit('parameters', { 'status': '200', 'parameters': parameters})

    @socketio.on('save_parameters')
    def handle_save_parameters(data):
        try:
            params_values = json.loads(data['parameters'])
            print(params_values)
            parameters = load_parameters()
            i = 0
            for key, value in parameters.items():
                print(key)
                if key == 'robot_name':                
                    value['value'] = params_values['robot_name']
                elif key != 'simulator_ids':     
                    value['value'] = int(params_values[key])
                i = i + 1

            save_parameters(parameters)
            emit('save_parameters_result', { 'status': '200', 'data': parameters})
        except Exception as e:
            print(e)
            emit('save_parameters_result', { 'status': 'error', 'data': 'parameters not saved'})

    @socketio.on('projects')
    def handle_projects():
        projects_list = get_all_projects()
        data = jsonify(projects_list)
        emit('projects', { 'status': '200', 'data': data })

    @socketio.on('new_project')
    def handle_new_project(data):
        title = data['title']
        info = data['info']
        project = Projects(title,info)
        db.session.add(project)
        db.session.commit()
        db.session.refresh(project)
        os.mkdir(os.path.join(Config.PROJECT_DIR,f'{project.project_id}'))
        shutil.copy(os.path.join(Config.APP_DIR,'assets/code_templates/template.xml'),os.path.join(Config.PROJECT_DIR,f'{project.project_id}/{project.project_id}.xml'))
        emit('new_project_result', { 'status': '200', 'project_id': project.project_id }) 

    @socketio.on('delete_project')
    def handle_delete_project(data):
        try:
            project_id = data['project_id']
            project = Projects.query.get(project_id)
            print(type(project))
            db.session.delete(project)
            db.session.commit()
            shutil.rmtree(os.path.join(Config.PROJECT_DIR,f'{project.project_id}'))
            emit('delete_project_result', {'status':'200', 'project_deleted': 'true' })
        except Exception as e:
            print(e)
            emit('delete_project_result', {'status':'error', 'project_deleted': 'false'})

    @socketio.on('edit_project')
    def handle_edit_project(project_id):
        try:
            project = Projects.query.get(project_id)
            project.title = request.args.get('title')    
            project.info = request.args.get('info')
            db.session.commit()       
            emit('edit_project', {'status':'updated'})
        except Exception as e:
            print(e)
            emit('edit_project', {'status':'error'})

    @socketio.on('script_status')
    def handle_script_status():
        if process_manager.get_process() is None or process_manager.get_process().poll() is not None:    
            emit('script_status',  {'status': 'completed'}) 
        else:
            emit('script_status',  {'status': 'still running'}) 


    @socketio.on('stop_script')
    def handle_stop_script():
        result = stop_now()
        emit('stop_script', result)

    @socketio.on('terminal_msgs')
    def handle_terminal_msgs(data):
        print(data)
        socketio.emit('trm',  data)

    def relay_to_robot(packet):
        socketio.emit('execute_fossbot',  packet)
        socketio.emit('get_fossbot_status')

    @socketio.on('fossbot_status')
    def on_connect(data):
        print("FossBot status: ", data)

    @socketio.on('execute_blockly')
    def handle_execute_blockly(data):
        relay_to_robot(json.dumps(data))
        socketio.emit('execute_blockly_robot', {'status': '200', 'result': 'Code saved with success'})
        try:
            id = data['id']
            code = data['code']
            print(code)
            print(Config.ROBOT_MODE)
            if Config.ROBOT_MODE=="coppelia":
                
                r = requests.get(url = 'http://127.0.0.1:23020/start')
                print(f'STart Coppelia {r}')
            try:
                stop_now()
                exec_process = Process(target=execute_blocks, args=(code,),daemon=True)
                exec_process.start()
                process_manager.set_process(exec_process)
            except Exception as e:
                print(e)
            emit('execute_blockly_result', {'status': '200'})
        except Exception as e:
            print(e)
            emit('execute_blockly_result',  {'status': '400'})

    @socketio.on('open_audio_folder')
    def open_audio_folder():
        os.startfile(os.path.realpath(os.path.join(Config.DATA_DIR,'sound_effects')))


    @socketio.on('open_stage_folder')
    def open_map_folder():
        os.startfile(os.path.realpath(os.path.join(Config.DATA_DIR,'Coppelia_Scenes')))

    @socketio.on('open_map')
    def open_map(data):
        print(data)
        if '.ttt' in data:
            stop_now()
            res = requests.get(url = 'http://localhost:23020/stop')
            print(f'Stop Coppelia {res}')
            coppelia_dir =  os.path.join(Config.DATA_DIR,'Coppelia_Scenes')
            scene_name =  os.path.join(coppelia_dir,data)
            print(scene_name)
            res = requests.post(url = 'http://localhost:23020/loadscene', data =scene_name)
            print(f'Load scene {res}')
        print('No map')

    @socketio.on('reset_stage')
    def reset_stage():
        res = requests.get(url = 'http://localhost:23020/stop')
        print(f'Stop Coppelia {res}')
        res = requests.get(url = 'http://localhost:23020/start')
        print(f'Start Coppelia {res}')

    @socketio.on('send_xml')
    def handle_send_xml(data):
        try:
            id = data['id']
            with open (os.path.join(Config.PROJECT_DIR,f'{id}/{id}.xml'), "r", encoding="utf8") as myfile:
                data=myfile.readlines()
            emit('send_xml_result', {'status': '200', 'data': data})   
        except Exception as e:
            emit('send_xml_result',  {'status': 'file not found'})

    @socketio.on('save_xml')
    def handle_save_xml(data):
        try: 
            id = data['id']
            code = data['code']        
            project = Projects.query.get(id)        
            code = code.replace('</xml>','')
            extra_info = ''.join(['  <project>\n', f'    <title>{project.title}</title>\n', f'    <description>{project.info}</description>\n', '  </project>\n', '</xml>'])
            code += extra_info
            with open(os.path.join(Config.PROJECT_DIR,f'{id}/{id}.xml'), "w", encoding="utf8") as fh:
                fh.write(code)
            emit('save_xml_result', {'status': '200', 'result': 'Code saved with success'})
        except Exception as e:
            emit('save_xml_result',  {'status': 'error occured', 'result': 'Code was not saved'})


    @socketio.on('systray_controls')
    def handle_systray_controls(message):
        if message['data'] == 'exit':
            imed_exit()
        else:
            print(message)   