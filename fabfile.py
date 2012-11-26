from fabric.api import sudo, cd, run
from fabric.context_managers import prefix
from cuisine import dir_exists, file_write, file_exists, upstart_ensure


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

def test_exists():
    with cd('~'):
        if not dir_exists('blogging'):
            print 'not exist'
        else:
            print 'exist'


def deploy():
    with cd('~'):
        if not dir_exists('blogging'):
            run('mkdir blogging')
            with cd('blogging'):
                run('git clone git://github.com/imathis/octopress.git')
                run('git clone git://github.com/tly1980/my_blog.git')

    with cd('~/blogging/octopress'):
        with prefix('source ~/.bash_profile'):
            run('bundle install')

    with cd('~/blogging/my_blog'):
        run('git pull')

    with cd('~/blogging/octopress'):
        run('rm Rakefile _config.yml config.rb')
        run('ln -s ../my_blog/Rakefile .')
        run('ln -s ../my_blog/_config.yml .')
        run('ln -s ../my_blog/config.rb .')

        with prefix('source ~/.bash_profile'):
            run('rake generate')

    sudo('ln -s ~/blogging/octopress/public /srv/keyonly.com')
    file_write('/etc/nginx/sites-available/keyonly.com', site_cfg, sudo=True)

    if not file_exists('/etc/nginx/sites-enabled/keyonly.com'):
        sudo('ln -s /etc/nginx/sites-available/keyonly.com /etc/nginx/sites-enabled/keyonly.com')

    upstart_ensure('nginx')
