import configparser

# https://wiki.python.org/moin/ConfigParserExamples

config = configparser.ConfigParser()
config.read("config.ini")

def get_scope_params():
    scope_A = {}
    scope_A['Type'] = config.get('Scope A', 'Type')
    scope_A['IP'] = config.get('Scope A', 'IP')
    
    scope_B = {}
    scope_B['Type'] = config.get('Scope B', 'Type')
    scope_B['IP'] = config.get('Scope B', 'IP')
    
    return scope_A, scope_B
    
def get_BB_params():
    BB = {}
    BB['IP'] = config.get('BeagleBone', 'IP')
    # Get pin configurations
    BB['Trigger'] = config.get('BeagleBone', 'Trigger')
    BB['MotorX_step'] = config.get('BeagleBone', 'MotorX_step')
    BB['MotorX_dir'] = config.get('BeagleBone', 'MotorX_dir')
    BB['MotorY_step'] = config.get('BeagleBone', 'MotorY_step')
    BB['MotorY_dir'] = config.get('BeagleBone', 'MotorY_dir')
    BB['MotorZ_step'] = config.get('BeagleBone', 'MotorZ_step')
    BB['MotorZ_dir'] = config.get('BeagleBone', 'MotorZ_dir')
    BB['X-pos'] = config.get('BeagleBone', 'X-pos')
    BB['Y-pos'] = config.get('BeagleBone', 'Y-pos')
    BB['Z-pos'] = config.get('BeagleBone', 'Z-pos')
    
    return BB