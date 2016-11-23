from peewee import fn
from random import randint

from db import Question as Question_db


class Question:

    def __init__(self, question_type=None, num_hints=3):

        self.question_type = question_type
        self.num_hints = num_hints

        self.question = {
            'qid': None,
            'question': None,
            'answer': None,
            'hints': []
        }

        if not question_type:

            q = self.random_question()

            self.question['qid'] = q.id
            self.question['question'] = q.question
            self.question['answer'] = q.answer
            self.question['hints'] = self.generate_hints(self.question['answer'], self.num_hints)

    @staticmethod
    def random_question():

        q = Question_db.select().where(Question_db.active).order_by(fn.Rand()).limit(1).get()

        return q

    @staticmethod
    def generate_hints(answer, num_hints):

        a = answer
        l = len(a)

        if l == 1:
            return ['*']

        elif l == 2:

            h = ['**']
            if randint(0, 1) == 0:
                h.append('*' + a[1])
            else:
                h.append(a[0] + '*')

            return h

        elif 3 <= l <= 5:
            hints = list()
            hint = list()

            for i in range(l):
                if a[i] != ' ':
                    hint.append('*')
                else:
                    hint.append(' ')

            hints.append("".join(hint))

            hint = list()

            for i in range(l):
                if (randint(0, 2) == 0) or a[i] == ' ':
                    hint.append(a[i])
                else:
                    hint.append('*')

            hints.append("".join(hint))

            return hints

        else:
            hints = list()

            hint = list()

            for i in range(l):
                if a[i] != ' ':
                    hint.append('*')
                else:
                    hint.append(' ')

            hints.append("".join(hint))

            hint = list()

            for i in range(l):
                if (randint(0, 1) == 0) or a[i] == ' ':
                    hint.append(a[i])
                else:
                    hint.append('*')

            hints.append("".join(hint))

            hint_comp = hint
            hint = list()

            for i in range(l):
                if (randint(0, 1) == 0) or a[i] == ' ' or hint_comp[i] != '*':
                    hint.append(a[i])
                else:
                    hint.append('*')

            hints.append("".join(hint))

            return hints

Question()

