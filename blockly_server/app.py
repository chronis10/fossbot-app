from flask import Flask,jsonify,request,Response, render_template,redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy_serializer import SerializerMixin
import os
import shutil
import yaml
from flask_socketio import SocketIO, emit
import glob
import json
import sys
import webbrowser
from xml.dom import minidom
from robot.roboclass import Agent
from multiprocessing import Process,freeze_support
from threading import Thread
from flask_babel import Babel
import pickle
import xml.etree.ElementTree as ET
import multiprocessing as mp
from multiprocessing import Process, Queue
import threading
import time


DOCKER = False
BASED_DIR = '/app' 
APP_DIR = '/app' 
if os.getenv('DOCKER') is not None:
    if os.getenv('DOCKER') == 'True':
        DOCKER = True

if not DOCKER:
    #from utils.systray_mode import systray_agent
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    BASED_DIR = os.path.abspath(os.path.dirname(sys.executable)) 

ROBOT_MODE  = 'coppelia'
if os.getenv('ROBOT_MODE') is not None:
    if os.getenv('ROBOT_MODE') == 'physical':
        ROBOT_MODE = 'physical'


DEBUG = True
if os.getenv('DEBUG') is not None:
    if os.getenv('DEBUG') == 'True':
        DEBUG = True

LOCALE = 'en'
if os.getenv('LOCALE') is None:
    LOCALE = 'en'
else:
    LOCALE = os.getenv('LOCALE')

SCRIPT_PROCCESS = None
COPPELIA_PROCESS = None
CURRENT_STAGE = None
app = Flask(__name__)

WORKERS_LIST = []
# Create an Event object
stopEvent = threading.Event()


DATA_DIR =  os.path.join(BASED_DIR,'data')
SQLITE_DIR = os.path.join(DATA_DIR,'robot_database.db')
PROJECT_DIR =os.path.join(DATA_DIR,'projects')
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SQLITE_DIR
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = LOCALE

CORS(app)
socketio = SocketIO(app)
db = SQLAlchemy(app)
agent = Agent()

class Projects(db.Model, SerializerMixin):
    project_id = db.Column('project_id', db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    info = db.Column(db.String(500))
    editor = db.Column(db.String(100))
    data = db.Column(db.Text)
    def __init__(self, title,info, editor, data=None):
        self.title = title
        self.info = info
        self.editor = editor
        self.data = data


def execute_blocks(code):
    agent.execute(code)
    
def execute_monaco(code):
    agent.execute(code)

def execute_code(code):
    agent.execute(code)

def get_locale():
    global LOCALE
    lan = request.cookies.get('locale')
    if lan is not None:
        LOCALE = lan
        app.config['BABEL_DEFAULT_LOCALE'] = lan
        return lan
    return request.accept_languages.best_match(['el', 'en'])

babel = Babel(app,locale_selector=get_locale)



# @app._got_first_request
def before_first_request(): 
    threading.Thread(target=monitor_workers_status, daemon=True).start()
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
        os.mkdir(PROJECT_DIR)
    elif not os.path.exists(PROJECT_DIR):
        os.mkdir(PROJECT_DIR)
    if ROBOT_MODE  == 'coppelia': 
        if not os.path.exists(os.path.join(DATA_DIR,'Coppelia_Scenes')):
            os.mkdir(os.path.join(DATA_DIR,'Coppelia_Scenes'))
    if not os.path.exists(os.path.join(DATA_DIR,'sound_effects')):
        shutil.copytree(os.path.join(APP_DIR,'utils/sound_effects'),os.path.join(DATA_DIR,'sound_effects'))

    db.create_all()    
    get_sound_effects()
    if not os.path.exists(os.path.join(DATA_DIR,'admin_parameters.yaml')):
        shutil.copy(os.path.join(APP_DIR,'utils/code_templates/admin_parameters.yaml'),os.path.join(DATA_DIR,'admin_parameters.yaml'))



@socketio.on('connection')
def on_connect(data):
    print("Socket connected, data received:", data)

@socketio.on('disconnection')
def on_disconnect(data):
    print("Socket disconnected!!, data received:", data)

@socketio.on_error()  
def error_handler(e):
    print('Error - socket  IO : ', e)

@app.route('/')
def index():
    
    stop_now()
    robot_name = get_robot_name()
    return render_template('home-page.html', robot_name=robot_name)

@socketio.on('get-all-projects')
def handle_get_all_projects():
    projects_list = get_all_projects()
    print('getting all projects')
    print(projects_list)

    emit('all-projects', { 'status': '200', 'data': projects_list})

def load_monaco_instrunctions(languange: str = 'en') -> dict: 
    path = os.path.join(APP_DIR,f'instructions/library_{languange}.json')
    with open(path) as json_file:
        data = json.load(json_file)
    return data


@app.route('/monaco')
def monaco():
    instructions = load_monaco_instrunctions('en')
    stop_now()
    id = request.args.get('id') 
    print("------------------>",id)
    robot_name = get_robot_name()
    get_sound_effects()
    scenes = get_scenes()
    locale = LOCALE
    return render_template('monaco.html', project_id=id, robot_name=robot_name,instructions=instructions,locale=locale,scenes=scenes)  

@app.route('/blockly')
def blockly():
    stop_now()
    id = request.args.get('id') 
    print("------------------>",id)
    robot_name = get_robot_name()
    get_sound_effects()
    scenes = get_scenes()
    locale = LOCALE
    return render_template('blockly.html', project_id=id, robot_name=robot_name,locale=locale,scenes=scenes)           

@app.route('/kindergarten')
def kindergarten():
    stop_now()
    robot_name = get_robot_name()
    scenes = get_scenes()
    return render_template('blockly_simple.html', project_id=-1, robot_name=robot_name,scenes=scenes)  

@socketio.on('get_sound_effects')
def blockly_get_sound_effects():
    if os.path.exists(os.path.join(DATA_DIR,'sound_effects.json')):
        with open(os.path.join(DATA_DIR,'sound_effects.json'), 'r') as file:
            sounds = json.load(file)
            emit('sound_effects',  { 'status': 200, 'data': sounds })
    else:
        emit('sound_effects', { 'status': 404, 'data': 'file does not exist'})       

@app.route('/admin_panel')
def admin_panel():
    stop_now()
    robot_name = get_robot_name()
    return render_template('panel-page.html', robot_name=robot_name,docker = DOCKER, mode = ROBOT_MODE)

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
    editor = data['editor']
    project = Projects(title, info, editor)
    db.session.add(project)
    db.session.commit()
    db.session.refresh(project)
    # os.mkdir(os.path.join(PROJECT_DIR,f'{project.project_id}'))
    # shutil.copy(os.path.join(APP_DIR,'utils/code_templates/template.xml'),os.path.join(PROJECT_DIR,f'{project.project_id}/{project.project_id}.xml'))
    emit('new_project_result', { 'status': '200', 'project_id': project.project_id }) 

@socketio.on('delete_project')
def handle_delete_project(data):
    try:
        project_id = data['project_id']
        project = Projects.query.get(project_id)
        print(type(project))
        db.session.delete(project)
        db.session.commit()
        # shutil.rmtree(os.path.join(PROJECT_DIR,f'{project.project_id}'))
        emit('delete_project_result', {'status':'200', 'project_deleted': 'true' })
    except Exception as e:
        print(e)
        emit('delete_project_result', {'status':'error', 'project_deleted': 'false', 'error_message': str(e)})

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
    global SCRIPT_PROCCESS
    if SCRIPT_PROCCESS is None or SCRIPT_PROCCESS.poll() is not None:       
        emit('script_status',  {'status': 'completed'}) 
    else:
        emit('script_status',  {'status': 'still running'}) 

@app.route('/stop_script')
def stop_script():
    result = stop_now()
    return jsonify(result)

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
    global SCRIPT_PROCCESS
    socketio.emit('execute_blockly_robot', {'status': '200', 'result': 'Code saved with success'})
    try:
        id = data['id']
        code = data['code']
        print(code)
        try:
            stop_script()
            SCRIPT_PROCCESS = Process(target=execute_blocks, args=(code,),daemon=True)
            SCRIPT_PROCCESS.start()
        except Exception as e:
            print(e)
        emit('execute_blockly_result', {'status': '200'})
    except Exception as e:
        print(e)
        emit('execute_blockly_result',  {'status': 'error when creating .py file or when running the .py file'})

# @socketio.on('execute_monaco')
# def handle_execute_monaco(data):
#     # relay_to_robot(json.dumps(data))
#     global SCRIPT_PROCCESS
#     # socketio.emit('execute_monaco_robot', {'status': '200', 'result': 'Code saved with success'})
#     try:
#         id = data['id']
#         code = data['code']
#         # print(code)
#         try:
#             stop_script()
#             SCRIPT_PROCCESS = Process(target=execute_monaco, args=(code,),daemon=True)
#             SCRIPT_PROCCESS.start()
#         except Exception as e:
#             print(e)
#         emit('execute_monaco_result', {'status': '200'})
#     except Exception as e:
#         print(e)
#         emit('execute_monaco_result',  {'status': 'error when creating .py file or when running the .py file'})

@socketio.on('execute_monaco')
def handle_execute_monaco(data):
    global WORKERS_LIST
    code = data['code']
    proc = Process(target=execute_code, args=(code,),daemon=True)
    WORKERS_LIST.append({'project_id': int(data['id']), 'user': 'default', 'process': proc, 'status': 'idle'})
    print(WORKERS_LIST)
    emit('execute_monaco_result', {'status': '200'})

@app.route('/classroom', methods=['GET'])
def classroom():
    global WORKERS_LIST
    serialized_workers = []
    for worker in WORKERS_LIST:
        serialized_worker = {
            'project_id': worker['project_id'],
            'user': worker['user'],
            'status': worker['status']
        }
        serialized_workers.append(serialized_worker)
    return render_template('classroom.html', workers=serialized_workers)
     
@socketio.on('runByID')
def handle_runByID(data):
    global WORKERS_LIST
    id = int(data['id']) - 1
  
    if len(WORKERS_LIST) == 0:
        emit('worker_result', {'status': 'error', 'message': 'Invalid worker ID'})
        return 

    if id >= len(WORKERS_LIST):
        emit('worker_result', {'status': 'error', 'message': 'Process ID out of range'})
        return 
    worker = WORKERS_LIST[id]

    if not worker['process'].is_alive():
        if worker['status'] == 'idle':
            if not any(worker['process'].is_alive() for worker in WORKERS_LIST if worker['status'] == 'active'):
                worker['process'].start()
                worker['status'] = 'active'

                emit('worker_result', {'status': 'success', 'message': f"Worker {id} started"})
                return
            else:
                emit('worker_result', {'status': 'error', 'message': "Another worker is running"})
                return
        elif worker['status'] == 'active':
            worker['status'] = 'finished'
            emit('worker_result', {'status': 'error', 'message': "Worker finished running"})
            return
        else:
            emit('worker_result', {'status': 'error', 'message': "Worker already finished"})
            return
    else:
        emit('worker_result', {'status': 'error', 'message': "Another worker is running"})
        return


def monitor_worker(id):
    global WORKERS_LIST

    worker = WORKERS_LIST[id]
    worker['process'].join()  # Wait for the worker process to complete
    worker['status'] = 'finished'


def monitor_workers_status():
    global WORKERS_LIST

    while True:
        for worker in WORKERS_LIST:
            if worker['status'] == 'active' and not worker['process'].is_alive():
                worker['status'] = 'finished'
        time.sleep(1)


def monitor_workers():
    global WORKERS_LIST
    global stopEvent

    # Check if there are any idle workers and start the next one
    for worker in WORKERS_LIST:
        if worker['status'] == 'idle':
            worker['process'].start()
            worker['status'] = 'active'
            while worker['status'] == 'active' and worker['process'].is_alive():
                time.sleep(1)
            if stopEvent.is_set():
                break

@socketio.on('stopByID')
def handle_stopByID(data):
    global WORKERS_LIST
    id = int(data['id']) - 1

    if len(WORKERS_LIST) == 0:
        emit('worker_result', {'status': 'error', 'message': 'Invalid worker ID'})
        return 

    if id >= len(WORKERS_LIST):
        emit('worker_result', {'status': 'error', 'message': 'Process ID out of range'})
        return
    
    worker = WORKERS_LIST[id]

    if worker['status'] == 'active':
        worker['process'].terminate()
        worker['status'] = 'finished'
        emit('worker_result', {'status': 'success', 'message': 'Worker stopped'})
        return
    elif worker['status'] == 'idle':
        emit('worker_result', {'status': 'error', 'message': 'Worker is not running'})
        return
    else:
        emit('worker_result', {'status': 'error', 'message': 'Worker already finished'})
        return

@socketio.on('deleteByID')
def handle_deleteByID(data):
    global WORKERS_LIST
    id = int(data['id']) - 1

    if len(WORKERS_LIST) == 0:
        emit('worker_result', {'status': 'error', 'message': 'Invalid worker ID'})
        return 

    if id >= len(WORKERS_LIST):
        emit('worker_result', {'status': 'error', 'message': 'Process ID out of range'})
        return
    
    worker = WORKERS_LIST[id]

    del WORKERS_LIST[id]
    emit('worker_result', {'status': 'success', 'message': 'Worker deleted'})
    emit('refresh_table', {'workers': WORKERS_LIST}, broadcast=True)  # Send updated data to all clients
    
    return

@socketio.on('runAllSerially')
def handle_runAllSerially():
    global WORKERS_LIST, stopEvent 

    if len(WORKERS_LIST) > 0:
        stopEvent.clear()
        threading.Thread(target=monitor_workers, daemon=True).start()
        emit('worker_result', {'status': 'success', 'message': 'Queue started'})
        return
    else:
        emit('worker_result', {'status': 'error', 'message': 'No workers available'})
        return

@socketio.on('stopAllQueue')
def handle_stopAllQueue():
    global WORKERS_LIST, stopEvent

    for worker in WORKERS_LIST:
        if worker['status'] == 'active':
            worker['process'].terminate()
            worker['status'] = 'finished'
            stopEvent.set()

    emit('worker_result', {'status': 'success', 'message': 'Queue stopped'})
    return


@socketio.on ('deleteAllFinished')
def handle_deleteAllFinished():
    global WORKERS_LIST

    WORKERS_LIST = [worker for worker in WORKERS_LIST if worker['status'] != 'finished']

    emit('worker_result', {'status': 'success', 'message': 'Finished workers deleted'})
    emit('refresh_table', {'workers': WORKERS_LIST}, broadcast=True)  # Send updated data to all clients
    return

@socketio.on('deleteAllQueue')
def handle_deleteAllQueue():
    global WORKERS_LIST

    WORKERS_LIST = []

    emit('worker_result', {'status': 'success', 'message': 'Queue cleared'})
    emit('refresh_table', {'workers': WORKERS_LIST}, broadcast=True)  # Send updated data to all clients
    return

@socketio.on('open_audio_folder')
def open_audio_folder():
    os.startfile(os.path.realpath(os.path.join(DATA_DIR,'sound_effects')))


@socketio.on('open_stage_folder')
def open_map_folder():
    os.startfile(os.path.realpath(os.path.join(DATA_DIR,'Coppelia_Scenes')))

@socketio.on('send_xml')
def handle_send_xml(data):
    try:
        id = data['id']
        project = db.session.query(Projects).get(id)
        serialized_data = project.data
        data = serialized_data

        # with open (os.path.join(PROJECT_DIR,f'{id}/{id}.xml'), "r", encoding="utf8") as myfile:
            # data=myfile.readlines()
        emit('send_xml_result', {'status': '200', 'data': data})   
    except Exception as e:
        print(e)
        emit('send_xml_result',  {'status': 'file not found'})

# @socketio.on('save_xml')
# def handle_save_xml(data):
#     try: 
#         id = data['id']
#         code = data['code']        
#         project = Projects.query.get(id)        
#         code = code.replace('</xml>','')
#         extra_info = ''.join(['  <project>\n', f'    <title>{project.title}</title>\n', f'    <description>{project.info}</description>\n', '  </project>\n', '</xml>'])
#         code += extra_info
#         with open(os.path.join(PROJECT_DIR,f'{id}/{id}.xml'), "w", encoding="utf8") as fh:
#             fh.write(code)
#         emit('save_xml_result', {'status': '200', 'result': 'Code saved with success'})
#     except Exception as e:
#         emit('save_xml_result',  {'status': 'error occured', 'result': 'Code was not saved'})


@socketio.on('save_xml')
def handle_save_xml(data):
    try: 
        id = data['id']
        code = data['code']        
        project = Projects.query.get(id) 
        project.data = code  
        db.session.add(project)
        db.session.commit()
        emit('save_xml_result', {'status': '200', 'result': 'Code saved with success'})
    except Exception as e:
        emit('save_xml_result',  {'status': 'error occured', 'result': 'Code was not saved'})
    

@app.route('/export_project/<int:id>')
def export_project(id):
    project_id = id

    # Fetch the code from the database.
    code = get_code_from_db(project_id)

    # If the code is not found, return a 404 error.
    if code is None:
        return Response(status=404)

    filename = f"tmp/{code['title']}.xml"

    # Create the root element
    root = ET.Element("project")

    # Add the attributes to the root element
    root.set("title", code["title"])
    root.set("info", code["info"])
    root.set("editor", code["editor"])

    # Create the data element
    data = ET.SubElement(root, "data")
    data.text = code["data"]

    # Create the XML tree
    tree = ET.ElementTree(root)
    path = os.path.join(APP_DIR, filename)
    print(path)

    # Save the XML tree to a file
    tree.write(path)

    # Serve the file, then delete it after serving.
    try:
        return send_file(path, as_attachment=True)
    finally:
        os.remove(path)


@app.route('/upload_project', methods=['POST'])
def upload_project():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect("/")

        file = request.files['file']
        if file.filename == '':
            return redirect("/")

        filename = file.filename
        if not filename.endswith('.xml'):
            return redirect("/")

        try:
            # Parse the XML file to get the root element
            tree = ET.parse(file)
            root = tree.getroot()

            # Extract the project attributes from the root element
            title = root.get("title")
            info = root.get("info")
            editor = root.get("editor")

            # Extract the data from the data element
            data = root.find("data").text

            project = Projects(title, info, editor, data)

            db.session.add(project)
            db.session.commit()
            db.session.refresh(project)

            return redirect("/")
        except ET.ParseError as e:
            return "Error: Invalid file format.", 400

    return redirect("/")


def get_code_from_db(project_id):
    project = Projects.query.get(project_id)
    if project:
        return {
            'editor': project.editor,
            'data': project.data,
            'title': project.title,
            'info': project.info
        }
    else:
        return None

def get_all_projects():
    projects = Projects.query.all()
    projects_list = [pr.to_dict() for pr in projects]
    return projects_list

def stop_now():
    global SCRIPT_PROCCESS
    print(SCRIPT_PROCCESS)
    print('stop')
    if SCRIPT_PROCCESS is None:
        return{'status': 'nothing running'}
    else:
        try:
            SCRIPT_PROCCESS.terminate()
            return {'status': 'stopped'}
        except Exception as e:
            print(e)
            return{'status': 'nothing running'}
        
def load_parameters():
    with open(os.path.join(DATA_DIR,'admin_parameters.yaml'), encoding=('utf-8')) as file:
        parameters = yaml.load(file, Loader=yaml.FullLoader)
    return parameters

def save_parameters(parameters):
    with open(os.path.join(DATA_DIR,'admin_parameters.yaml'), 'w', encoding=('utf-8')) as file:
        parameters = yaml.dump(parameters, file)

def get_robot_name():
    parameters = load_parameters()
    for key, value in parameters.items():
        if(key == "robot_name"):
            print("Getting robot name: ", value['value'] )
            return value['value']
    return " "

def get_scenes():
    files = glob.glob(os.path.join(DATA_DIR,'Coppelia_Scenes/*.ttt')) 
    names = [item.split("\\")[-1] for item in files]
    return names

def get_sound_effects():
    print("Getting sounds")    
    if os.path.exists(os.path.join(DATA_DIR,'sound_effects')):
        mp3_sounds_list = glob.glob(os.path.join(DATA_DIR,'sound_effects/*.mp3'))
        sounds_names = []
        for sound in mp3_sounds_list: 
            split_list = os.path.split(sound)
            audio_name = split_list[-1]
            audio_name_list = audio_name.split(".")
            audio_name = audio_name_list[0]
            sounds_names.append({ "sound_name": audio_name, "sound_path": os.path.normpath(sound)})        
        print("sound effects:")        
        #delete first the json file if exists and then create it again 
        if os.path.exists(os.path.join(DATA_DIR,'sound_effects.json')):
            os.remove(os.path.join(DATA_DIR,'sound_effects.json'))
        with open(os.path.join(DATA_DIR,'sound_effects.json'), 'w') as out_file:
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

@app.route("/shutdown")
def shutdown():
    imed_exit()

@socketio.on('systray_controls')
def handle_systray_controls(message):
    if message['data'] == 'exit':
        imed_exit()
    else:
        print(message)


if __name__ == '__main__':
    freeze_support()

    if not DOCKER:
        # systray = Thread(target=systray_agent,daemon=True)
        # systray.start()
        pass
        # webbrowser.open_new("http://127.0.0.1:8081")
    with app.app_context():
        before_first_request()
    socketio.run(app, host = '0.0.0.0',port=8081, debug=DEBUG)
