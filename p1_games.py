class Game:
    def __init__(self, id, title, price):
        self.id = id
        self.title = title
        self.price = int(price)

    def str(self):
        return f"{id}) {self.title}     Price: {self.price}"
