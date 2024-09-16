from .models import Notification

def Notification_non_lue(request):
    if request.user.is_authenticated:
        return {
            'Notification_non_lue': Notification.objects.filter(destinataire=request.user, est_lu=False).count()
        }
    return {}
