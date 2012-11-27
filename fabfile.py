from fabric.api import sudo, cd, local
from fabric.context_managers import prefix, settings, lcd
from cuisine import dir_exists, file_write, file_exists, upstart_ensure, run
import os

site_cfg = """
server {
    server_name    www.keyonly.com    keyonly.com  keyonly.test;
    access_log /var/log/nginx/keyonly.access.log;
    index index.html index.htm;

    location / {
        root /srv/keyonly.com/;
        try_files $uri $uri/ /index.html;
    }
}
"""


def gen():
    o_path = os.path.realpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
            '..', 'octopress')
    )

    with lcd(o_path):
        local('rake generate')


def test_exists():
    with cd('~'):
        if not dir_exists('blogging'):
            print 'not exist'
        else:
            print 'exist'


def deploy(commit_msg=None):
    if commit_msg:
        localpath = os.path.dirname(os.path.realpath(__file__))
        with lcd(localpath):
            with settings(warn_only=True):
                local('git commit -am "{commit_msg}"'.format(commit_msg=commit_msg))
                local('git push')

    with cd('~'):
        if not dir_exists('blogging'):
            run('mkdir blogging')
            with cd('blogging'):
                run('git clone git://github.com/imathis/octopress.git')
                run('git clone git://github.com/tly1980/my_blog.git')

    with cd('~/blogging/octopress'):
        with prefix('source ~/.bash_profile'):
            # install the desire ruby version
            run('bundle install')

    with cd('~/blogging/my_blog'):
        run('git pull')

    with cd('~/blogging/octopress'):
        with settings(warn_only=True):
            run('rm Rakefile _config.yml config.rb source')

        run('ln -s ../my_blog/Rakefile .')
        run('ln -s ../my_blog/_config.yml .')
        run('ln -s ../my_blog/config.rb .')
        run('ln -s ../my_blog/source .')
        run('rake generate')

    with cd('~'):
        with settings(warn_only=True):
            sudo('rm -rvf /srv/keyonly.com')

        sudo('cp -r blogging/octopress/public /srv/keyonly.com')
        sudo('chmod -R 0755 /srv/keyonly.com')

    file_write('/etc/nginx/sites-available/keyonly.com', site_cfg, sudo=True)
    if not file_exists('/etc/nginx/sites-enabled/keyonly.com'):
        sudo('ln -s /etc/nginx/sites-available/keyonly.com /etc/nginx/sites-enabled/keyonly.com')

    upstart_ensure('nginx')
