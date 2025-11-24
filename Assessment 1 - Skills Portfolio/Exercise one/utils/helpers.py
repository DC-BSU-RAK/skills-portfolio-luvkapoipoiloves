import random

class MathHelper:
    @staticmethod
    def calculate_result(number1, number2, operation):
        if operation == '+':
            return number1 + number2
        elif operation == '-':
            return number1 - number2
        elif operation == '*':
            return number1 * number2
        return 0

class PowerUpManager:
    def __init__(self):
        self.available_boosts = 3
        
    def use_boost(self):
        if self.available_boosts > 0:
            self.available_boosts -= 1
            return True
        return False
        
    def reset_boosts(self):
        self.available_boosts = 3