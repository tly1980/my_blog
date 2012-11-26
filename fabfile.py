from fabric.api import sudo, cd
from cuisine import dir_exists, file_write, file_exists, upstart_ensure


site_cfg = """
server {
    server_name    www.keyonly.com    keyonly.com  keyonly.test;
    access_log /var/log/nginx/keyonly.access.log;
    index index.html index.htm;

    location ~ ^/my_blog/(.+) {
        root /srv/my_blog/;
        satisfy any;
    }

    location / {
        root /srv/my_blog/;
        try_files $uri $uri/ /index.html;
    }


}
"""


def deploy():
    if not dir_exists('/srv/my_blog'):
        with cd('/srv/'):
            sudo('git clone git://github.com/tly1980/my_blog.git')

    with cd('/srv/my_blog'):
        sudo('git pull')

    file_write('/etc/nginx/sites-available/keyonly.com', site_cfg, sudo=True)

    if not file_exists('/etc/nginx/sites-enabled/keyonly.com'):
        sudo('ln -s /etc/nginx/sites-available/keyonly.com /etc/nginx/sites-enabled/keyonly.com')

    upstart_ensure('nginx')
