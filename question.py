from random import randint

questions = [
            [1, "1 + 1?", "2"],
            [2, "100 - 6?", "94"],
            [3, "3 * 12?", "36"]
            ]


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

            self.question['qid'] = q[0]
            self.question['question'] = q[1]
            self.question['answer'] = q[2]

            self.question['hints'] = self.generate_hints(self.question['answer'], self.num_hints)

            print(self.question)

        else:
            print(self.question)


    @staticmethod
    def random_question():

        qid = randint(0, len(questions) - 1)
        q = questions[qid]

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
        else:
            disguised = '*' * l
            h = []
            i = 0
            while i < 3:
                h_temp = list(disguised)
                for j in h_temp:
                    if randint(0, 1) == 0:
                        h_temp[j] = answer[j]
                    h.append(h_temp)
                i += 1
            return h
