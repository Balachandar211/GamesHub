from  .microservices import mail_service
from GamesHub.celery import app

@app.task(name='send_daily_email')
def send_daily_email():
    status, message = mail_service(
        Subject='Daily Update',
        message='This is your scheduled email.',
        recepients=['balachandarspl@gmail.com', 'shinjoblal@gmail.com']
    )
