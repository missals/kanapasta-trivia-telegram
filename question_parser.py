import os

from config.db import db, Question

DIRECTORY = 'raw_questions/'

# list files
files = os.listdir(DIRECTORY)

i = 1
j = 0

questions = []

for file in files:
    with open(DIRECTORY + file, 'r', encoding='cp1252', errors='ignore') as f:
        for line in f:

            raw_line = line.rstrip('\n')
            question = raw_line.split('*')

            # Pick easy questions with just one answer
            if (len(question) == 2) and (question[0][:4] != 'KAOS'):

                # Create a dict for the question
                q = {'question': question[0].encode('utf-8'), 'answer': question[1].encode('utf-8'), 'group': str(file)}
                questions.append(q)

                j += 1

            i += 1

print(j)

# Save questions to db
with db.atomic():
    for idx in range(0, len(questions), 100):
        Question.insert_many(questions[idx:idx+100]).execute()
        print("Saved 100 rows!")
