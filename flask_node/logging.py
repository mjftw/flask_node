import os

class Logging():
    def log(self, message, file=None):
        print(message)

        if file:
            with open(file, 'a') as f:
                f.write(message + '\n')
