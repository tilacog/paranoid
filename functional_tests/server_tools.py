import subprocess
from os import path

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

def send_fixture_file(host, filepath):
    subprocess.check_call(
        [
            'fab',
            'send_fixture_file:filepath={}'.format(filepath),
            '--host={}'.format(host),
            # '--hide=everything,status',
        ],
        cwd=THIS_FOLDER
    )

def create_media_file_on_server(host):
    return subprocess.check_call(  # expect fabric to return the newfile path
        [
            'fab',
            'create_media_file',
            '--host={}'.format(host),
        ]
        cwd=THIS_FOLDER
    )
