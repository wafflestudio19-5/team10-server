source ~/.zshrc

cd /home/ec2-user/team10-server
git checkout master --quiet
git pull origin master

cd /home/ec2-user/team10-server/soundcloud
source venv/bin/activate
pip3 install -r requirements.txt --quiet

python3 manage.py migrate
python3 manage.py check --deploy

pkill -f gunicorn
gunicorn soundcloud.wsgi --bind 127.0.0.1:8000 --daemon
sudo nginx -t
sudo service nginx restart