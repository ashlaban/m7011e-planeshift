#!/usr/bin/env python3
from app import db, models

u = models.User(username='john', password='pass', email='john@email.com')
db.session.add(u)
db.session.commit()
