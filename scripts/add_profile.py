from main.models import Profile
from django.contrib.auth.models import User

#parameter set player instructions
for u in User.objects.all():
    if hasattr(u, 'profile'):
        continue
    p = Profile(user=u)
    u.profile = p
    u.profile.save()
    u.save()
    
