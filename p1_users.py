from ssl import _create_unverified_context


class User:
    def __init__(self, username, pw, fname, lname, role, credit):
        self.username = username
        self.pw = pw
        self.fname = fname
        self.lname = lname
        self.role = role
        self.credit = credit

    def str(self):
        return f"Username: {self.username}, First name: {self.fname}, Last name: {self.lname}, role: {self.role}, credit: {self.credit}"
