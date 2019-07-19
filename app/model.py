def initialize_database(db):
    class Users(db.Model):
        id = db.Column(db.Integer, primary_key = True)


    class Set(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        type = db.Column(db.Integer)
        name = db.Column(db.Integer)
        active = db.Column(db.Boolean) 

        def __init__(self, type, name, active):
            self.type = type
            self.name = name
            self.active = active


    class Page(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        uuid = db.Column(db.String(200))

        def __init__(self, uuid):
            self.uuid = uuid


    class Annotations(db.Model):
        id = db.Column(db.Integer, primary_key = True)
        set_id = db.Column(db.Integer)
        user_id = db.Column(db.Integer)
        record_id = db.Column(db.Integer) 
        annotation = db.Column(db.String(50))
        time = db.Column(db.DateTime)

        def __init__(self, name, city, addr, pin):
            self.set_id     = set_id
            self.user_id    = user_id
            self.record_id  = record_id
            self.annotation = annotation
            #self.time =


    class Records(db.Model):
        id =        db.Column(db.Integer, primary_key = True)
        position =  db.Column(db.Integer)
        set_id =    db.Column(db.Integer)
        page_id_1 = db.Column(db.Integer)
        page_id_2 = db.Column(db.Integer)
        page_id_3 = db.Column(db.Integer)
        page_id_4 = db.Column(db.Integer)
        page_id_5 = db.Column(db.Integer)
        page_id_6 = db.Column(db.Integer)

        def __init__(self, position, set_id, page_id_1, 
                     page_id_2=None, page_id_3=None, page_id_4=None, page_id_5=None, page_id_6=None):
            self.position  = position
            self.set_id    = set_id
            self.page_id_1 = page_id_1
            self.page_id_2 = page_id_2
            self.page_id_3 = page_id_3
            self.page_id_4 = page_id_4
            self.page_id_5 = page_id_5
            self.page_id_6 = page_id_6