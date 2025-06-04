import random

class Game:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.current_question = None

    def reset(self):
        self.score = 0
        self.level = 1
        self.current_question = None

    def increment_score(self):
        self.score += 1
        # 每5分提升难度
        if self.score % 5 == 0:
            self.level += 1

    def generate_question(self):
        # 根据等级生成题目
        max_num = 10 + self.level * 5
        a = random.randint(1, max_num)
        b = random.randint(1, max_num)
        self.current_question = {
            'text': f"{a} + {b} = ?",
            'answer': str(a + b)
        }
        return self.current_question

    def check_answer(self, answer: str) -> bool:
        if not self.current_question:
            return False
        return answer.strip() == self.current_question['answer']
