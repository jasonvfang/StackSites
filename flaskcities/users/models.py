from flaskcities.database import db, CRUDMixin
from flaskcities.extensions import bcrypt


class User(CRUDMixin, db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    pwdhash = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime())
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.created_at = datetime.utcnow()
        self.set_password(password)
    
    def set_password(self, password):
        self.pwdhash = bcrypt.generate_password_hash(password)
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.pwdhash, password)
        
    def __repr__(self):
        return "<User ({0}, id: {1})>".format(self.username, self.id)