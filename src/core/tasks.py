from main.celery import app
from core.utils import recordatorio_templates, enviar_encuesta_palumbo
from core.models import *
from celery import shared_task


# @app.task(bind=True, name='tasks.core.test_task')
# def test_task(self):
#     print("HOLA")
#     return True

# @app.task(bind=True, name='tasks.core.recordatorio_templates')
# def recordatorio_templates_celery(self, suscripcion_whatsapp_id, recordatorio_id):
#     recordatorio_templates(suscripcion_whatsapp_id, recordatorio_id)
#     return True

# @app.task(bind=True, name='tasks.core.enviar_encuesta_palumbo_celery')
# def enviar_encuesta_palumbo_celery(self):
#     enviar_encuesta_palumbo()
#     return True
