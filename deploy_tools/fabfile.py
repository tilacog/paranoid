import random

from fabric.api import env, local, run, settings
from fabric.contrib.files import append, exists, sed


REPO_URL = 'https://github.com/tilacog/paranoid.git'
PLUGIN_REPO_URL = 'git@bitbucket.org:tilacog/titan_plugins.git'

# TODO: Put gunicorn under supervisor control
# The following deploy steps are currently made manually:
    # Create/Update nginx config file
    # Create/Update gunicorn config file
    # Create/Update celery supervisor config file
    # Create/Update rabbitmq supervisor config file
    # Create rabbitmq v_host
    # Restart Gunicorn
    # Restart Celery

def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _get_latest_plugin_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run('mkdir -p %s/%s' % (site_folder, subfolder))


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, source_folder))
    current_commit = local('git log -n 1 --format=%H', capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))


def _get_latest_plugin_source(source_folder):
    plugin_folder = source_folder.replace('source', 'plugins')
    if exists(plugin_folder+ '/.git'):
        run('cd %s && git fetch' % (plugin_folder,))
    else:
        run('git clone %s %s' % (PLUGIN_REPO_URL, plugin_folder))
    current_commit = local(
        'git -C ../plugins log -n 1 --format=%H', capture=True
    )
    run('cd %s && git reset --hard %s' % (plugin_folder, current_commit))


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/paranoid/settings.py'

    # Let DEBUG=True on staging server
    if not 'staging' in env.host:
        sed(settings_path, 'DEBUG = True', 'DEBUG = False')

    # Update DOMAIN to match site_name
    sed(settings_path, 'DOMAIN = "localhost"', 'DOMAIN = "%s"' % (site_name,))

    # Import a new SECRET_KEY name with a randomly generated value
    secret_key_file = source_folder + '/paranoid/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

    # Update BROKER_URL to point to the correct (rabbitmq) v_host
    v_host = '/staging' if 'staging' in env.host else '/main'
    broker_url = 'amqp://guest@localhost:5672/' + v_host
    sed(settings_path, 'amqp://', broker_url)


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/requirements.txt' % (
            virtualenv_folder, source_folder
    ))


def _update_static_files(source_folder):
    run('cd %s && ../virtualenv/bin/python3 manage.py collectstatic --noinput' %(
        source_folder,
    ))


def _update_database(source_folder):
    run('cd %s && ../virtualenv/bin/python3 manage.py migrate --noinput' % (
        source_folder,
    ))
