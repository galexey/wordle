from __future__ import annotations

#import sched
#from sysconfig import scheme
from typing import TYPE_CHECKING, List, Set, Dict, Tuple, Union, Any, Optional, NewType, Callable, Hashable
import sys, getopt



def get_words(filename:str, wordlen:int = 5)->List[str]:
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
    opts, args = getopt.getopt(argv, "hwkent", ["help", "wordlistfilename=", "known=", "exclude_lettesr=", "number_of_letters=", "testit"])
    filename= None
    number_of_letters = 5
    exclude=""
    just_do_tests = False
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print("findwords.py --wordlistfilename <filename> \n[--known <known_parts>] [--number_of_letters <number>] [--exclude_lettesr <letters_not_in_the_word>\n known_parts in the form: \n   *: unknown letter\n   lowercase letter: letter is in word, but position is wrong \n   UPPERCASE LETTER: letter and position is correct")
            sys.exit()
        elif opt in ["--w", "--wordlistfilename"]:
           filename = arg
        elif opt in ["--k", "--known"]:
            known=arg.split(",")
            #known=arg
        elif opt in ["--e", "--exclude_letters"]:
            exclude=arg
        elif opt in ["--n", "--number_of_letters"]:
            number_of_letters=int(arg)
        elif opt in ["--t", "--testit"]:
            just_do_tests = True
    if just_do_tests:
        do_test()
        return


    known = [".i.en",".EI.."]
    #known=["Ri...",".r..s"]

    exclude ="rtdch"
    for a_known in known:
        if len(a_known) != number_of_letters:
            print("all known should have {} letters, but '{}' has {} letters !".format(number_of_letters,a_known, len(a_known)))
            return
        for a_letter in a_known:

            if a_letter.lower() in exclude:
                print("you defined that the letter '{}' is in the word, but also defined that the letter is excluded ({})!".format(a_letter, exclude))
                return


    the_words=get_words(filename=filename,wordlen=number_of_letters)
    # outfile=open("5_letter_words.txt", 'w')
    # outfile.write('\n'.join(the_words) + '\n')
    # outfile.close()
    letter_probability=[
            "E",
            "N",
            "I",
            "S",
            "R",
            "A",
            "T",
            "D",
            "H",
            "U",
            "L",
            "C",
            "G",
            "M",
            "O",
            "B",
            "W",
            "F",
            "K",
            "Z",
            "P",
            "V",
            "ẞ",
            "J",
            "Y",
            "X",
            "Q"]
    possible_words=the_words
    for a_known in known:
        possible_words = get_words_that_match(all_possible_words= possible_words,known= a_known,exclude= exclude)

    print(possible_words)



if __name__ == "__main__":
    # debugpy.listen(("0.0.0.0", 5678))
    #print(sys.argv[1:])
    main(sys.argv[1:])