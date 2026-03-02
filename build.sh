#!/usr/bin/env bash
set -euo pipefail

cd BACKEND

python manage.py migrate
python manage.py collectstatic --noinput

python manage.py shell -c "
from api.models import User
u, created = User.objects.get_or_create(
    username='kitwana26',
    defaults={'role': 'admin', 'is_staff': True, 'is_superuser': True}
)
u.role = 'admin'
u.is_staff = True
u.is_superuser = True
u.set_password('2002')
u.save()
print('admin created' if created else 'admin updated')
"
