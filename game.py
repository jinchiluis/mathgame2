import random

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.current_question = None
        self.questions_answered = 0  # Track total questions answered
        self.time_limit = 10  # Current time limit for the question

    def increment_score(self):
        self.score += 1
        self.questions_answered += 1
        self.update_time_limit()

    def update_time_limit(self):
        """Update time limit based on questions answered"""
        if self.questions_answered <= 5:
            self.time_limit = 10  # 10 seconds for first 5 questions
        elif self.questions_answered <= 10:
            self.time_limit = 7   # 7 seconds for questions 6-10
        elif self.questions_answered <= 20:
            self.time_limit = 5   # 5 seconds for questions 11-20
        elif self.questions_answered <= 25:
            self.time_limit = 3   # 3 seconds for questions 21-25
        else:
            self.time_limit = 1   # 1 second for questions 26+

    def generate_question(self):
        """Generate a question based on current score"""
        # Only multiplication until 10th question, then add division
        if self.questions_answered < 10:
            self.current_question = self.generate_multiplication()
        else:
            # After 10th question, randomly choose between multiplication and division
            operation = random.choice(['multiplication', 'division'])
            if operation == 'multiplication':
                self.current_question = self.generate_multiplication()
            else:
                self.current_question = self.generate_division()

        return self.current_question

    def generate_multiple_choice_options(self, correct_answer):
        """Generate 4 unique multiple choice options including the correct answer"""
        options = [correct_answer]

        # Generate 3 incorrect options
        while len(options) < 4:
            # Create plausible wrong answers
            if correct_answer <= 5:
                # For small numbers, add/subtract small amounts
                wrong = correct_answer + random.choice([-3, -2, -1, 1, 2, 3])
            elif correct_answer <= 20:
                # For medium numbers, vary more
                wrong = correct_answer + random.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
            else:
                # For larger numbers, vary by percentage
                variation = max(1, int(correct_answer * random.uniform(0.1, 0.3)))
                wrong = correct_answer + random.choice([-variation, variation])
                
            # Ensure positive numbers and no duplicates
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        # Shuffle the options so correct answer isn't always first
        random.shuffle(options)
        
        return options

    def generate_multiplication(self):
        """Generate multiplication question (numbers 1-10)"""
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        correct_answer = a * b
        options = self.generate_multiple_choice_options(correct_answer)
        
        return {
            'text': f"{a} × {b} = ?",
            'answer': correct_answer,
            'options': options
        }

    def generate_division(self):
        """Generate division question (ensuring whole number result, numbers 1-10)"""
        # Generate the answer first, then create the division
        quotient = random.randint(1, 10)
        divisor = random.randint(2, 10)  # Divisor between 2-10
        dividend = quotient * divisor  # This ensures clean division
        correct_answer = quotient
        options = self.generate_multiple_choice_options(correct_answer)

        return {
            'text': f"{dividend} ÷ {divisor} = ?",
            'answer': correct_answer,
            'options': options
        }

    def check_answer(self, selected_answer) -> bool:
        if not self.current_question:
            return False
        return selected_answer == self.current_question['answer']

    def get_current_operations(self):
        """Return list of currently available operations for display"""
        if self.questions_answered < 10:
            return ['Multiplication']
        else:
            return ['Multiplication', 'Division']

    def get_time_remaining_message(self):
        """Get a descriptive message about time limits"""
        if self.questions_answered < 5:
            return f"⏱️ 时间限制: {self.time_limit} 秒 (第 {self.questions_answered + 1}/5 题 - 练习阶段)"
        elif self.questions_answered < 10:
            return f"⏱️ 时间限制: {self.time_limit} 秒 (第 {self.questions_answered + 1}/10 题 - 开始加速)"
        elif self.questions_answered < 20:
            return f"⏱️ 时间限制: {self.time_limit} 秒 (第 {self.questions_answered + 1} 题 - 快速模式)"
        elif self.questions_answered < 25:
            return f"⏱️ 时间限制: {self.time_limit} 秒 (第 {self.questions_answered + 1} 题 - 极速挑战!)"
        else:
            return f"⏱️ 时间限制: {self.time_limit} 秒 (第 {self.questions_answered + 1} 题 - 闪电模式!!)"
