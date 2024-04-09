from flask import Blueprint, render_template, request, redirect, jsonify, send_file
from extensions import db
import os
from app.db_models.models import Projects
from config import Config
from app.control_utils.utils import stop_now, get_robot_name, get_scenes, get_sound_effects, imed_exit
from xml.dom import minidom
import platform
# Create a Blueprint
routes_bp = Blueprint('routes_bp', __name__)

@routes_bp.route('/')
def index():
    stop_now()
    robot_name = get_robot_name()
    return render_template('home-page.html', robot_name=robot_name)

def shared_blockly_logic(project_id=None, kindergarten=False):
    stop_now()
    id = request.args.get('id') if project_id is None else project_id

    print("------------------>", id)
    robot_name = get_robot_name()
    scenes = get_scenes()
    locale = Config.LOCALE
    return render_template('editors/blockly.html', project_id=id, robot_name=robot_name, scenes=scenes,locale=locale, robot_mode=Config.ROBOT_MODE, kindergarten=kindergarten)

@routes_bp.route('/blockly')
def blockly():
    return shared_blockly_logic()

@routes_bp.route('/kindergarten')
def kindergarten():
    return shared_blockly_logic(project_id=-1, kindergarten=True)

@routes_bp.route("/shutdown")
def shutdown():
    imed_exit()

@routes_bp.route('/admin_panel')
def admin_panel():
    stop_now()
    cur_platform = platform.system()
    data_path = Config.DATA_DIR
    robot_name = get_robot_name()
    return render_template('panel-page.html', robot_name=robot_name,docker = Config.DOCKER, mode = Config.ROBOT_MODE, cur_platform=cur_platform, data_path=data_path)

@routes_bp.route('/stop_script')
def stop_script():
    result = stop_now()
    return jsonify(result)

@routes_bp.route('/export_project/<int:id>')
def export_project(id):
    print(id)
    path = os.path.join(Config.PROJECT_DIR,f'{id}/{id}.xml')
    return send_file(path, as_attachment=True)

@routes_bp.route('/upload_project', methods=[ 'POST'])
def upload_project():    
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect("/")
        file = request.files['file']
        if file.filename == '':
            return redirect("/")
        data = file.read().decode('utf-8')
        docs = minidom.parseString(data)
        pjs = docs.getElementsByTagName('project')[0]
        title = pjs.getElementsByTagName('title')[0].firstChild.data
        info = pjs.getElementsByTagName('description')[0].firstChild.data
        project = Projects(title,info)
        db.session.add(project)
        db.session.commit()
        db.session.refresh(project)        
        os.mkdir(os.path.join(Config.PROJECT_DIR,f'{project.project_id}'))
        with open(os.path.join(Config.PROJECT_DIR,f'{project.project_id}/{project.project_id}.xml'), "w", encoding="utf8") as fh:
            fh.write(data)
    return redirect("/")
