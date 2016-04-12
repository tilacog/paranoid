import random

from fabric.api import env, local, put, run, settings, sudo
from fabric.contrib.files import append, exists, sed

REPO_URL = 'https://github.com/tilacog/paranoid.git'
PLUGIN_REPO_URL = 'git@bitbucket.org:tilacog/titan_plugins.git'

# The following deploy steps are currently made manually:
    # Create/Update nginx config file
    # Create/Update gunicorn supervisor config file
    # Create/Update celery supervisor config file
    # Create/Update rabbitmq supervisor config file
    # Create rabbitmq v_host

def deploy():
    settings_file = 'paranoid.settings.' + (
        'staging' if 'staging' in env.host else 'production'
    )
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    source_folder = site_folder + '/source'

    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _get_latest_plugin_source(source_folder)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder, settings_file)
    _update_database(source_folder, settings_file)
    _send_secrets_file(source_folder)
    _supervisorctl_restart()


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

def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/requirements.txt' % (
            virtualenv_folder, source_folder
    ))

def _update_static_files(source_folder, settings_file):
    command = ('cd {dir} && ../virtualenv/bin/python3 manage.py collectstatic'
               ' --noinput --settings={settings}')
    run(command.format(dir=source_folder, settings=settings_file))

def _update_database(source_folder, settings_file):
    command = ('cd {dir} && ../virtualenv/bin/python3 manage.py migrate'
               ' --noinput --settings={settings}')
    run(command.format(dir=source_folder, settings=settings_file))

def _send_secrets_file(source_folder):
    put('paranoid/settings/secrets.ini',
        source_folder + '/paranoid/settings/secrets.ini'
    )

def _supervisorctl_restart():
    program_group = (
        'staging' if 'staging' in env.host else 'production'
    )
    sudo("supervisorctl restart %s:" % (program_group,))
