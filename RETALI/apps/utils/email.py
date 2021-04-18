import logging
from smtplib import SMTPException
from django.core.mail import send_mail
from RETALI.settings import ADMINS, EMAIL_HOST_USER

CONFIRMATION_EMAIL_SUBJECT = "Confirmación de correo electrónico"
RECOVER_PASSWORD_SUBJECT = "Restablece tu contraseña de RETALI"
ERROR_ALERT = "Ocurrio un error importante en RETALI"

logger = logging.getLogger(__name__)


class Email:
    """ Clase para enviar correos """

    def __init__(self, asunto, mensaje, cliente, mensaje_html=''):
        self.asunto = asunto
        self.mensaje = mensaje
        self.email_host = EMAIL_HOST_USER
        self.cliente = [cliente]
        self.mensaje_html = mensaje_html

    @staticmethod
    def _obtener_emails_de_administradores():
        """ Obtiene los emails de los administradores"""
        admins = ADMINS
        emails = []
        for admin in admins:
            emails.append(admin[1])
        return emails

    @classmethod
    def enviar_mensaje_de_error(cls, error):
        """ Envia un mensaje de error a los administradores"""
        asunto = ERROR_ALERT
        mensaje = error
        admins_email = Email._obtener_emails_de_administradores()
        for email_admin in admins_email:
            email = Email(asunto, mensaje, email_admin)
            email.enviar_correo()

    def enviar_correo(self):
        """ Metodo para enviar un correo """
        try:
            send_mail(
                subject=self.asunto,
                message=self.mensaje,
                from_email=self.email_host,
                recipient_list=self.cliente,
                fail_silently=False,
                html_message=self.mensaje_html,
            )
        except SMTPException as ex:
            logger.error(f'Error al enviar correo {str(ex)}')
