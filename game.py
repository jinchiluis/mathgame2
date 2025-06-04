import random

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.current_question = None
        # Separate max numbers for each operation type
        self.max_num_add = 10
        self.max_num_sub = 10
        self.max_num_mul = 10
        self.max_num_div = 10

    def increment_score(self):
        self.score += 1
        
        # Increase difficulty more gradually
        self.max_num_add += 1  # Addition difficulty increases with each score
        
        # Increase difficulty for unlocked operations more slowly
        if self.score >= 10:
            if self.score % 2 == 0:  # Every 2 points after score 10
                self.max_num_sub += 1

        if self.score >= 20:
            if self.score % 3 == 0:  # Every 3 points after score 20
                self.max_num_mul += 1

        if self.score >= 30:
            if self.score % 4 == 0:  # Every 4 points after score 30
                self.max_num_div += 1

    def generate_question(self):
        """Generate a question based on current score"""
        # Determine available operations based on score
        operations = ['addition']

        if self.score >= 10:
            operations.append('subtraction')
        if self.score >= 20:
            operations.append('multiplication')
        if self.score >= 30:
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
        if self.score >= 10:
            operations.append('Subtraction')
        if self.score >= 20:
            operations.append('Multiplication')
        if self.score >= 30:
            operations.append('Division')
        return operations
