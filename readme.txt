readme 

# error logs
root@ubuntu-s-1vcpu-512mb-10gb-sfo3-01:~# cat /var/log/fw29/fw29_log.out.log
root@ubuntu-s-1vcpu-512mb-10gb-sfo3-01:~# cat /var/log/fw29/fw29_log.err.log

# Enter virtual env
source env/bin/activate

# Secure copy to droplet
scp -r api.py root@64.23.140.231:/root/fw29
scp -r data root@64.23.140.231:/root/fw29

# Reloading droplet
sudo supervisorctl reload
sudo systemctl restart nginx

# Droplet IP
http://64.23.140.231/

# An affirmation that you exist

# gunicorn bind app
gunicorn --bind=0.0.0.0 api:app
gunicorn -w 3 api:app

# install requirements
pip install -r requirements.txt

# make requirements.txt
pip freeze > requirements.txt