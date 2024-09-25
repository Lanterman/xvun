from django.core.mail import send_mail

from celery import shared_task

from config import settings


@shared_task
def send_reset_password(user_email: str, secret_key: str) -> None:
    html_message = f"""
        <p>
            Request to reset user password with email '{user_email}'.\n 
            To reset your password, follow the link:\n
            <h3>http://127.0.0.1:8000/api/v1/auth/reset_password/{user_email}/{secret_key}</h3>
        </p>
    """

    send_mail(
        subject=f'Request to change user password',
        message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
        fail_silently=False,
        html_message=html_message,
    )
