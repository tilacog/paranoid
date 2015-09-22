from fabric.api import env, run

def _get_base_folder(host):
    return '~/sites/' + host

def _get_manage_dot_py(host):
    return '{path}/virtualenv/bin/python {path}/source/manage.py'.format(
        path=_get_base_folder(host)
    )

def reset_database():
    run('{manage_py} flush --noinput'.format(
        manage_py=_get_manage_dot_py(env.host)
    ))

def create_session_on_server(email, password):

    cmd_string = (
        "{manage_py} create_session_cookie "
        "--email={email} --password={password}"
    )

    serialized_cookie= run(cmd_string.format(
        manage_py=_get_manage_dot_py(env.host),
        email=email,
        password=password,
    ))

    print(serialized_cookie)
