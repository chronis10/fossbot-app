import os

class Config:
    # DOCKER configuration
    DOCKER = True #os.getenv('DOCKER','False') == 'True'

    # Directories configuration
    #BASE_DIR = os.getenv('BASE_DIR', '/app' if DOCKER else os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    #APP_DIR = os.getenv('APP_DIR', '/app' if DOCKER else os.path.abspath(os.path.dirname(__file__)))
    #DATA_DIR =os.path.join(os.getenv('DATA_DIR', BASE_DIR), 'data')
    BASE_DIR = "/home/pi/.local/lib/python3.9/site-packages/blockly_server"
    APP_DIR = "/home/pi/.local/lib/python3.9/site-packages/blockly_server"
    DATA_DIR = os.path.join("/home/pi", 'data')
    PROJECT_DIR = os.path.join(DATA_DIR, 'projects')
    ADMIN_PARAMS = os.path.join(DATA_DIR, 'admin_parameters.yaml')


    # Robot configuration
    ROBOT_MODE = os.getenv('ROBOT_MODE', 'coppelia')
    

    # Database configuration
    SQLITE_DIR = os.path.join(DATA_DIR, 'robot_database.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', f'sqlite:///{SQLITE_DIR}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Languange configuration
    LOCALE = os.getenv('LOCALE', 'en')
    if 'LOCALE' not in os.environ:
      os.environ['LOCALE'] = 'en'
    BABEL_DEFAULT_LOCALE = LOCALE
    #BABEL_DEFAULT_Config.LOCALE = LOCALE

    # Host and Port 
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8081'))
    BROWSER_HOST = os.getenv('BROWSER_HOST', 'localhost')
   
    # Debug configuration
    DEBUG = os.getenv('DEBUG', 'True') == 'False'

    # Austostart web browser
    AUTOSTART_BROWSER  = os.getenv('AUTOSTART_BROWSER', 'True') == 'True'

    # # CoppeliaSim configuration
    # COPPELIA_PATH = os.getenv('COPPELIA_PATH', '/home/chronis/CoppeliaSim_Edu_V4_6_0_rev18_Ubuntu20_04')
    # COPPELIA_HEADLESS = os.getenv('COPPELIA_HEADLESS', 'True') == 'False'
                              

    
