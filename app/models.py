from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from app import app

# Defining followers and followed users.
followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)
class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key = True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    ## Many-to-many relationship
    """
    Both relationships are defined with the so.WriteOnlyMapped type
    > secondary configures the association table that is used for this relationship, which I defined right above this class.
    > primaryjoin indicates the condition that links the entity to the association table. In the following relationship, the user has to match the follower_id attribute of the association table, so the condition reflects that.
    >  The followers.c.follower_id expression references the follower_id column of the association table. In the followers relationship, the roles are reversed, so the user must match the followed_id column.
    > secondaryjoin indicates the condition that links the association table to the user on the other side of the relationship. In the following relationship, the user has to match the followed_id column, and in the followers relationship, the user has to match the follower_id column. 
    """
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')

    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')    
    
    ## Adding and removing followers
    """
    The is_following() method performs a query on the following relationship to see if a given user is already included in it. All write-only relationships have a select() method that constructs a query that returns all the elements in the relationship. 

    The followers_count() and following_count() methods return the follower and following counts for the user. The sa.select() clause for these queries specify the sa.func.count() function from SQLAlchemy, to indicate that I want to get the result of a function. 

    The select_from() clause is then added with the query that needs to be counted. Whenever a query is included as part of a larger query, SQLAlchemy requires the inner query to be converted to a sub-query by calling the subquery() method.
    """
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(followers.c.followed_id == user.id)
        return db.session.scalar(query) is not None
    
    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(query)
    
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery()
        )
        return db.session.scalar(query)
    
    ## Following post query
    """
    The select() portion of the query defines the entity that needs to be obtained, which in this case is posts. What I'm doing next is joining the entries in the posts table with the Post.author relationship.

    A join is a database operation that combines rows from two tables, according to a given criteria temporarily. When the join() clause is given a relationship as an argument, SQLAlchemy combines the rows from the left and right sides of the relationship.

    Effectively, what the join above does is create an extended table that provides access to posts, along with information about the author of each post.

    To be able to clearly tell SQLAlchemy how to join all these tables, I need to have a way to refer to users independently as authors and as followers. The so.aliased() calls are used to create two references to the User model that I can use in the query.
    """
    def following_posts(self):
        Author = so.aliased(User) # To combine the posts with their authors
        Follower = so.aliased(User) # To combine the posts with their followers
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author)) # Matches the posts of their respective users
            .join(Author.followers.of_type(Follower), isouter=True) # The isouter=True option tells SQLAlchemy to use a left outer join instead, which preserves items from the left side that have no match on the right.
            .where(sa.or_(
                Follower.id == self.id, # or is a conditional statement
                Author.id == self.id
            )) # Filters unnecessary posts
            .group_by(Post) # This clause looks at the results after filtering has been done, and eliminates any duplicates of the provided arguments. 
            .order_by(Post.timestamp.desc()) # Sorting
        )
    
    ## Resetting Password
    """
    The get_reset_password_token() function returns a JWT token as a string, which is generated directly by the jwt.encode() function.
    The verify_reset_password_token() is a static method, which means that it can be invoked directly from the class.
    """
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)
class Post(db.Model):
    """
    The new Post class will represent blog posts written by users. The timestamp field is defined with a datetime type hint and is configured to be indexed, which is useful if you want to efficiently retrieve posts in chronological order. 

    The user_id field was initialized as a foreign key to User.id, which means that it references values from the id column in the users table. Since not all databases automatically create an index for foreign keys, the index=True option is added explicitly, so that searches based on this column are optimized.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return f'<Posts {self.body}'

# Because Flask-Login knows nothing about databases, it needs the application's help in loading a user.
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

