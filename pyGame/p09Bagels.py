"""
Mastermind clone
Guess the number
"""
import random

NUM_DIGITS = 3
MAX_GUESS = 10

def getSecretNum():
    # retunrs a string of unique random digits
    numbers = list(range(10))
    random.shuffle(numbers)
    secretNum = ''
    for i in range(NUM_DIGITS):
        secretNum += str(numbers[i])
    return secretNum

def getClues(guess, secretNum):
    if guess == secretNum:
        return "You got it!"

    clues = []
    for i in range(len(guess)):
        if guess[i] == secretNum[i]:
            clues.append('Fermi!')
        elif guess[i] in secretNum:
            clues.append('Pico.')
    if len(clues) == 0:
        return "Bagels"
    clues.sort()
    return ' '.join(clues)
                
def isOnlyDigits(num):
    # return true if only digits in passed string
    if num == '':
        return False
    for i in num:
        if i not in '0 1 2 3 4 5 6 7 8 9'.split():
            return False
    return True

def game():
    print ('Instructions')

    while True:
        secretNum = getSecretNum()
        print (f"I have the number, you have {MAX_GUESS} to find it")
        guessesTaken = 1
        while guessesTaken <= MAX_GUESS:
            guess = ''
            while len(guess) != NUM_DIGITS or not isOnlyDigits(guess):
                print (f"Guess #{guessesTaken}:")
                guess = input()

                print (getClues(guess, secretNum))
                guessesTaken += 1

                if guess == secretNum:
                    break
                if guessesTaken > MAX_GUESS:
                    print (f"Ran out of guesses for {secretNum}")

        print ("Play again?")
        if not input().lower().startswith('y'):
            break

def main():
    game()
    # for _ in range(5):
    #     a = getSecretNum()
    #     b = getSecretNum()
    #     print (f"g:{a} s:{b}  {isOnlyDigits(a)} {isOnlyDigits(b)} {getClues(a, b)} ")

    # a= '3e3'
    # b = 'x0x'
    # print (f"g:{a} s:{b}  {isOnlyDigits(a)} {isOnlyDigits(b)} {getClues(a, b)} ")


if __name__ == "__main__":
    main()