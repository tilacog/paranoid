import random

from fabric.api import env, local, run, settings
from fabric.contrib.files import append, exists, sed

REPO_URL = 'https://github.com/tilacog/paranoid.git'

def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)
    
    # Will do the steps below manually
    #_create_nginx_config_file(env.host, source_folder)
    #_create_gunicorn_upstart_file(env.host, source_folder)
    #_restart_nginx_and_gunicorn(env.host)

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

def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/paranoid/settings.py'
    if not 'staging' in env.host:  # Let DEBUG=True on staging server
        sed(settings_path, 'DEBUG = True', 'DEBUG = False')
    sed(settings_path, 'DOMAIN = "localhost"', 'DOMAIN = "%s"' % (site_name,))
    secret_key_file = source_folder + '/paranoid/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

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

def _create_nginx_config_file(site_name, source_folder):
    # Get nginx.conf template file from source and use sed to update site name
    run('sed "s/SITENAME/{site_name}/g" '
        '{source_folder}/deploy_tools/nginx.template.conf | '
        'sudo tee /etc/nginx/sites-available/{site_name}'.format(
            site_name=site_name,
            source_folder=source_folder,
    ))

    # Create a symlink on nginx config directories, if it doesn't exist yet
    with settings(warn_only=True):
        cmd_string = (
            'sudo ln -s /sites-available/{site_name} '
            '/etc/nginx/sites-enabled/{site_name}'
        )

        run(cmd_string.format(site_name=site_name))

def _create_gunicorn_upstart_file(site_name, source_folder):
    # Get gunicorn.conf template from source and use sed to update site name
    run('sed "s/SITENAME/{site_name}/g" '
        '{source_folder}/deploy_tools/gunicorn-upstart.template.conf | '
        'sudo tee /etc/init/gunicorn-{site_name}.conf'.format(
            site_name=site_name,
            source_folder=source_folder,
    ))

def _restart_nginx_and_gunicorn(site_name):
    # Starts or restart/reload nginx and gunicorn
    run('sudo service nginx reload')

    with settings(warn_only=True):
        gunicorn_cmd = run ('sudo restart gunicorn-%s' % (site_name,))
    if gunicorn_cmd.failed:
        run ('sudo start gunicorn-%s' % (site_name,))
