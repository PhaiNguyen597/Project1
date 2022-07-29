class Game:
    def __init__(self, id, title, price):
        self.id = int(id)
        self.title = title
        self.price = float(price)

    def str(self):
        return f"{id}) {self.title}     Price: {self.price}"
