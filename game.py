import random

class Game:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.current_question = None
        # Separate max numbers for each operation type
        self.max_num_add = 10
        self.max_num_sub = 10
        self.max_num_mul = 10
        self.max_num_div = 10

    def reset(self):
        self.score = 0
        self.level = 1
        self.current_question = None
        self.max_num_add = 10
        self.max_num_sub = 10
        self.max_num_mul = 10
        self.max_num_div = 10

    def increment_score(self):
        self.score += 1
        # Every 5 points, increase level and difficulty
        if self.score % 5 == 0:
            self.level += 1
            self.max_num_add += 5

            # Increase difficulty for unlocked operations more slowly
            if self.level >= 10:
                if self.score % 10 == 0:  # Every 10 points after level 10
                    self.max_num_sub += 3

            if self.level >= 20:
                if self.score % 15 == 0:  # Every 15 points after level 20
                    self.max_num_mul += 2

            if self.level >= 30:
                if self.score % 20 == 0:  # Every 20 points after level 30
                    self.max_num_div += 2

    def generate_question(self):
        """Generate a question based on current level"""
        # Determine available operations based on level
        operations = ['addition']

        if self.level >= 10:
            operations.append('subtraction')
        if self.level >= 20:
            operations.append('multiplication')
        if self.level >= 30:
            operations.append('division')

        # Randomly select an operation
        operation = random.choice(operations)

        if operation == 'addition':
            self.current_question = self.generate_addition()
        elif operation == 'subtraction':
            self.current_question = self.generate_subtraction()
        elif operation == 'multiplication':
            self.current_question = self.generate_multiplication()
        elif operation == 'division':
            self.current_question = self.generate_division()

        return self.current_question

    def generate_addition(self):
        """Generate addition question"""
        a = random.randint(1, self.max_num_add)
        b = random.randint(1, self.max_num_add)
        return {
            'text': f"{a} + {b} = ?",
            'answer': str(a + b)
        }

    def generate_subtraction(self):
        """Generate subtraction question (ensuring positive result)"""
        a = random.randint(1, self.max_num_sub)
        b = random.randint(1, self.max_num_sub)
        # Ensure a >= b for positive result
        if a < b:
            a, b = b, a
        return {
            'text': f"{a} - {b} = ?",
            'answer': str(a - b)
        }

    def generate_multiplication(self):
        """Generate multiplication question"""
        a = random.randint(1, self.max_num_mul)
        b = random.randint(1, self.max_num_mul)
        return {
            'text': f"{a} × {b} = ?",
            'answer': str(a * b)
        }

    def generate_division(self):
        """Generate division question (ensuring whole number result)"""
        # Generate the answer first, then create the division
        quotient = random.randint(1, self.max_num_div)
        divisor = random.randint(2, min(self.max_num_div, 12))  # Keep divisor reasonable
        dividend = quotient * divisor  # This ensures clean division

        return {
            'text': f"{dividend} ÷ {divisor} = ?",
            'answer': str(quotient)
        }

    def check_answer(self, answer: str) -> bool:
        if not self.current_question:
            return False
        return answer.strip() == self.current_question['answer']

    def get_current_operations(self):
        """Return list of currently available operations for display"""
        operations = ['Addition']
        if self.level >= 10:
            operations.append('Subtraction')
        if self.level >= 20:
            operations.append('Multiplication')
        if self.level >= 30:
            operations.append('Division')
        return operations
