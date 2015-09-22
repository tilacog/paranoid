from os import path
import subprocess
THIS_FOLDER = path.dirname(path.abspath(__file__))


def create_session_on_server(host, email, password):
    return subprocess.check_output(
        [
            'fab',
            'create_session_on_server:email={},password={}'.format(
                email, password
            ),
            '--host={}'.format(host),
            '--hide=everything,status',
        ],
        cwd=THIS_FOLDER
    ).decode().strip()

def reset_database(host):
    subprocess.check_call(
        ['fab', 'reset_database', '--host={}'.format(host)],
        cwd=THIS_FOLDER
    )

def create_user_on_server(host, email, password):
    subprocess.check_call(
        [
            'fab',
            'create_user:email={},password={}'.format(
                email, password
            ),
            '--host={}'.format(host),
            '--hide=everything,status',
        ],
    cwd=THIS_FOLDER
    )
