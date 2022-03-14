from __future__ import annotations

#import sched
#from sysconfig import scheme
from typing import TYPE_CHECKING, List, Set, Dict, Tuple, Union, Any, Optional, NewType, Callable, Hashable
import sys, getopt



def get_words(filename:str, wordlen:int = 5, allowed_letters:str = None)->List[str]:
    if allowed_letters is None: allowed_letters="ABCDEFGHIJKLMNOPQRSTUVW"
    allowed_letters_upper=allowed_letters.upper()
    def is_letters_ok(word:str):
        for l in word:
            if l.upper() not in allowed_letters_upper:
                return False
        return True
    result = []
    file = open(filename, 'r')
    while True:
        word = file.readline()
        if not word:
            break
        word=word.lower()
        word = word[:-1]
        word=word.replace("ö","oe")
        word=word.replace("ü", "ue")
        word=word.replace("ä", "ae")
        word=word.replace("ß", "sz")

        if len(word) == wordlen:
            if is_letters_ok(word):
                result.append(word)

    return result

def does_it_fit(known:str, test:str, exclude_letters:str=None):

    if exclude_letters is not None:
        for c in exclude_letters:
            if c in test:
                return False

    letterindex = 0
    for letter in known:
        try:
            if letter.isupper():
                if test[letterindex] != letter.lower():
                    return False
                else:
                    continue
            if letter.islower():
                if letter not in test:
                    return False



                if test[letterindex] == letter.lower():
                    # we know that letter is in the word, but the position is wrong. so if we have that letter in that position, test cant be the right one.
                    return False

                # we know that letter is in the word, but the position is wrong. Lets see if test fits
                did_match = False
                for idx, testletter in enumerate(test):
                    if testletter != letter:
                        continue
                    if known[idx].isupper():
                        continue
                    if letter == testletter:
                        did_match = True
                        break
                if not did_match:
                    return False
        finally:
            letterindex += 1
    return True

def does_it_fit_for_suggestions(shall_include:str, word_to_test:str,  exclude_letters:str=None):
    if exclude_letters is not None:
        for c in exclude_letters:
            if c in word_to_test:
                return False
    letterindex = 0
    for letter in shall_include:
        try:
            if letter.isupper():
                if word_to_test[letterindex] == letter.lower():
                    return False
                else:
                    continue
            if letter.islower():
                if letter not in word_to_test:
                    return False

                # we know that letter is in the word, but the position is wrong. Lets see if test fits
                did_match = False
                for idx, testletter in enumerate(word_to_test):
                    if testletter != letter:
                        continue
                    if shall_include[idx].isupper():
                        continue
                    if letter == testletter:
                        did_match = True
                        break
                if not did_match:
                    return False
        finally:
            letterindex += 1
    return True




def get_suggestions(all_possible_words:List[str],shall_include:str,exclude:str="",letterprobability:Dict[str:float]=None):
    if letterprobability is None:

        letter_probability = {
            "E":17.4,
            "N":9.78,
            "I":7.55,
            "S":7.27,
            "R":7.0,
            "A":6.51,
            "T":6.15,
            "D":5.08,
            "H":4.76,
            "U":4.35,
            "L":3.44,
            "C":3.06,
            "G":3.01,
            "M":2.53,
            "O":2.51,
            "B":1.89,
            "W":1.89,
            "F":1.66,
            "K":1.21,
            "Z":1.13,
            "P":0.79,
            "V":0.67,
            "J":0.27,
            "Y":0.04,
            "X":0.03,
            "Q":0.02}

    possible_words = []
    for a_shall_include in shall_include:
        for a_word_to_test in all_possible_words:
            if does_it_fit_for_suggestions(shall_include=a_shall_include, word_to_test=a_word_to_test, exclude_letters=exclude):
                possible_words.append(a_word_to_test)

    # now calculate_probability
    word_probs: Dict[str,float] = {}
    for a_word in possible_words:
        prob = 0
        for i, a_letter in enumerate(a_word):
            if a_letter in a_word[:i]:
                continue
            prob += letter_probability[a_letter.upper()]
        word_probs[a_word]=prob

    pro_result = dict(sorted(word_probs.items(), key=lambda item: item[1],reverse=True))

    return pro_result


def get_words_that_match(all_possible_words:List[str],known:str,exclude:str=""):
    result=[]
    for a_word_to_test in all_possible_words:
        if does_it_fit(known=known,test=a_word_to_test,exclude_letters=exclude):
            result.append(a_word_to_test)
    return result

def do_test():
    def test_word(known:str, test:str, exclude_letters:str, expect_fit:bool):
        assert does_it_fit(known=known, test=test, exclude_letters=exclude_letters) == expect_fit, "expected testword '{test_word}' {fitornot} to fit.".format(test_word=test, fitornot= "NOT" if not expect_fit else "")

    test_word("T.ase", "aaaaa", "", False)
    test_word("T.a..", "tasse", "", True)
    test_word("Tsa..", "tasse", "", True)
    test_word("Tsa.s", "tasse", "", True)
    test_word("Tsaes", "tasse", "", True)
    test_word("TsaSE", "tasse", "", True)
    test_word("TsASE", "tasse", "", False)
    test_word("TsasE", "tasse", "", False)
    test_word("tasse", "tasse", "", False)
    test_word(".....", "tasse", "", True)
    test_word("TASSE", "tasse", "", True)
    test_word("....E", "tasse", "", True)




def main(argv):
    opts, args = getopt.getopt(argv, "hwdkentsa", ["help", "wordlistfilename=", "dictionaryfilename=", "known=", "exclude_letters=", "number_of_letters=", "testit", "suggest_words", "allowed_letters="])
    filename= None
    dictionary_filename = None
    number_of_letters = 5
    exclude=""
    just_do_tests = False
    known = None
    suggest_words = False
    allowed_letters = None
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print("findwords.py --wordlistfilename <filename> \n--dictionaryfilename <filename>\n[--known <known_parts>] \n[--number_of_letters <number>] \n[--exclude_letters <letters_not_in_the_word>\n known_parts in the form: \n   *: unknown letter\n   lowercase letter: letter is in word, but position is wrong \n   UPPERCASE LETTER: letter and position is correct")
            print("e.g. create a 5-words file list based on a dictionary in the folder 'wordlist': findwords.py --wordlistfilename x5_letter_words.txt --dictionaryfilename './wordlist/german.dic' --n 5")
            print("\n e.g. find words based on the wordlistfile '5_letter_words.txt' with 5 letters based on the following hints:\n  there is an 'R' in the word, but not on the first place, \n  there is a 'E' in the word, but not in the 5th place")
            print("  there is a 'F' in the first place!!! (so you got that letter right already),\n  there is a 'R' but not on the 3rd, \n  there is a 'D', but not at 4th, \n  there is a 'E' but not at the 5th place. :")
            print("  the following letters are NOT part to the word:'itnba')"
                  "--wordlistfilename 5_letter_words.txt --n 5 --known r..e.,F.rde --exclude_letters itnba")
            sys.exit()
        elif opt in ["--w", "--wordlistfilename"]:
           filename = arg
        elif opt in ["--d", "--dictionaryfilename"]:
           dictionary_filename = arg
        elif opt in ["--a", "--allowed_letters"]:
           allowed_letters = arg
        elif opt in ["--k", "--known"]:
            known=arg.split(",")
            #known=arg
        elif opt in ["--e", "--exclude_letters"]:
            exclude=arg
        elif opt in ["--n", "--number_of_letters"]:
            number_of_letters=int(arg)
        elif opt in ["--t", "--testit"]:
            just_do_tests = True
        elif opt in ["--s", "--suggest_words"]:
            suggest_words = True
    if just_do_tests:
        do_test()
        return


    #known = [".i.en",".EI.."]
    #known=["Ri...",".r..s"]

    #exclude ="rtdch"
    if allowed_letters == None:
        allowed_letters = "ABCDEFGHIJKLMNOPQRSTUVW"
        print("no allowed_letters defined. using default: '{}'".format(allowed_letters))

    if dictionary_filename is not None:
        #we create a wordlist_file
        if filename is None:
            print("no wordfilelist defined")
            return



        print("creating wordfile list '{}' with {}-letterwords from '{}'".format(filename,number_of_letters,dictionary_filename))
        the_words = get_words(dictionary_filename,allowed_letters,number_of_letters)
        outfile=open(filename, 'w')
        outfile.write('\n'.join(the_words) + '\n')
        outfile.close()
        print("successfully created '{}' with {}-letterwords from '{}'".format(filename,number_of_letters,dictionary_filename))
        return
    if filename is None:
        print("no wordlist specified!")
        return

    if known is None or len(known)==0:
        print("no known words specified!")
        return
    for a_known in known:
        if len(a_known) != number_of_letters:
            print("all known should have {} letters, but '{}' has {} letters !".format(number_of_letters,a_known, len(a_known)))
            return
        for a_letter in a_known:

            if a_letter.lower() in exclude:
                print("you defined that the letter '{}' is in the word, but also defined that the letter is excluded ({})!".format(a_letter, exclude))
                return

    the_words = get_words(filename=filename, wordlen=number_of_letters)

    if suggest_words:
        print("suggesting to try the following words:")
        suggestions = get_suggestions(all_possible_words=the_words,shall_include=known,exclude=exclude)
        print("suggestions to test:")
        for word,prob in suggestions.items():
            print("{}:{}".format(word,round(prob,2)))

        return


    possible_words = the_words

    print("possible words:")
    for a_known in known:
        possible_words = get_words_that_match(all_possible_words=possible_words, known=a_known, exclude=exclude)

    print(possible_words)




    # outfile=open("5_letter_words.txt", 'w')
    # outfile.write('\n'.join(the_words) + '\n')
    # outfile.close()







if __name__ == "__main__":
    # debugpy.listen(("0.0.0.0", 5678))
    #print(sys.argv[1:])
    main(sys.argv[1:])