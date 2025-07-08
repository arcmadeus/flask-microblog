from app import app, db
from app.models import User, Post
import sqlalchemy as sa

query = sa.select(User)
users = db.session.scalars(query).all()
for u in users:
    print(u.id, u.username)