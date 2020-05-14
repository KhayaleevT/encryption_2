import pickle
import argparse
import sys
from collections import Counter

alphabets = [(ord('a'), ord('z')), (ord('а'), ord('я')), (ord(' '), ord('@')), (ord('['), ord('`')),
             (ord('{'), ord(''))]


def upper_alpha(alpha):
    return ord(chr(alpha[0]).upper()), ord(chr(alpha[1]).upper())


def _get_alpha(_chr):
    _ord = ord(_chr.lower())
    global alphabets
    for alpha in alphabets:
        if alpha[0] <= _ord <= alpha[1]:
            return (alpha[0], alpha[1]) if _chr.islower() else upper_alpha(alpha)
    return None


def is_letter(_chr):
    _ord = ord(_chr.lower())
    global alphabets
    for alpha in alphabets[0:2]:
        if alpha[0] <= _ord <= alpha[1]:
            return True
    return False


def _same_alphabets(alpha1, alpha2):
    return chr(alpha1[0]).lower() == chr(alpha2[0]).lower()


def _shift_ord(_chr, shift, _alpha=None):
    if shift == 0:
        return _chr
    if _alpha is None:
        _alpha = _get_alpha(_chr)
    numb = ord(_chr)
    if _alpha:
        numb = numb - _alpha[0]
        numb = _alpha[0] + (numb + shift) % (_alpha[1] + 1 - _alpha[0])
        return chr(numb)
    return _chr


def _caesar(file, key: int):
    ans = []
    for line in file:
        for ch in line:
            ans.append(_shift_ord(ch, key))
    return ''.join(ans)


MIN_ORD = 32


def _vernam_xor(ch, xor_ch):
    """32 is ord of ' ' """
    xor_1 = ord(ch) - MIN_ORD
    xor_2 = ord(xor_ch) - MIN_ORD
    return chr((xor_1 ^ xor_2) + MIN_ORD)


def _vernam(file, key):
    ans = []
    ch_num = 0
    for line in file:
        for ch in line:
            if ord(ch) < MIN_ORD:
                ans.append(ch)
                continue
            _shift_chr = key[ch_num]
            ch_num += 1
            ans.append(_vernam_xor(ch, _shift_chr))
    return ''.join(ans)


def _vigenere(file, key, _cipher=1):
    """_cipher parameter means the direction of what we are doing, 1 means cipher, -1 means decipher"""
    ans = []
    ch_num = 0
    for line in file:
        for ch in line:
            ch_alpha = _get_alpha(ch)
            if ch_alpha:
                _shift_chr = key[ch_num % len(key)]
                ch_num += 1
                _shift_alpha = _get_alpha(_shift_chr)
                if _shift_alpha:
                    ans.append(_shift_ord(ch, _cipher * (ord(_shift_chr) - _shift_alpha[0]), ch_alpha))
                else:
                    ans.append(ch)
            else:
                ans.append(ch)
    return ''.join(ans)


def vernam_encode(file, key: str):
    return _vernam(file, key)


def vernam_decode(file, key: str):
    return _vernam(file, key)


def caesar_decode(file, key: int):
    return _caesar(file, -key)


def caesar_encode(file, key: int):
    return _caesar(file, key)


def vigenere_encode(file, key: str):
    return _vigenere(file, key)


def vigenere_decode(file, key: str):
    return _vigenere(file, key, -1)


def _first_file_letters(file, shift=0, _max_amount=40000):
    """40000 is just random big number,you can put 1000000 or 500000 here as well"""
    _processed = 0
    for line in file:
        for _ch in line:
            shift_ch = _shift_ord(_ch, shift)
            if is_letter(shift_ch):
                yield shift_ch
                _processed += 1
        if _processed > _max_amount:
            break


def _frequencies(file):
    _letters = dict()
    _letters = Counter(_ch for _ch in _first_file_letters(file))
    data_amount = sum(_letters.values())
    for ch in _letters:
        _letters[ch] /= data_amount
    return _letters


def _dump_frequencies(freqs, _file='frequencies.txt'):
    with open(_file, 'wb') as fr:
        pickle.dump(freqs, fr)


def _load_frequencies(_file='frequencies.txt'):
    with open(_file, 'rb') as fr:
        return pickle.load(fr)


def _freq_diff(freqs1, freqs2):
    diff = 0
    for _alpha in alphabets[0:2]:
        for i in range(_alpha[0], _alpha[1] + 1):
            _chr = chr(i)
            freq1 = freqs1[_chr] if _chr in freqs1 else 0
            freq2 = freqs2[_chr] if _chr in freqs2 else 0
            diff += ((freq1 - freq2) ** 2)
    return diff


def _caesar_count_freq(file, key: int):
    """Counting frequencies of text encoded in caesar with the key"""
    ans = Counter(_ch for _ch in _first_file_letters(file, key))
    let_amount = sum(ans.values())
    for ch in ans:
        ans[ch] /= let_amount
    file.seek(0)
    return ans


def caesar_hack(file, freqs):
    best_key = min((_freq_diff(_caesar_count_freq(file, -key), freqs), key) for key in range(0, 33))[1]
    return caesar_decode(file, best_key)


def _encode(args):
    _input = _get_input_and_ready_output(args)
    cipher, key = _get_cipher_and_key(args)
    if cipher == "caesar":
        print(caesar_encode(_input, int(key)), end='')
    elif cipher == "vigenere":
        print(vigenere_encode(_input, key), end='')
    else:
        print(vernam_encode(_input, key), end='')


def _decode(args):
    _input = _get_input_and_ready_output(args)
    cipher, key = _get_cipher_and_key(args)
    if cipher == "caesar":
        print(caesar_decode(_input, key), end='')
    elif cipher == "vigenere":
        print(vigenere_decode(_input, key), end='')
    else:
        print(vernam_decode(_input, key), end='')


def _get_input_and_ready_output(args):
    if args.output:
        sys.stdout = open(args.output, 'w', encoding='utf-8')
    _input = open(args.input, 'r', encoding='utf-8') if args.input else sys.stdin
    return _input


CIPHERS = {"vigenere", "caesar", "vernam"}


def _get_cipher_and_key(args):
    cipher = args.cipher
    if cipher is None or cipher not in CIPHERS:
        cipher = "caesar"
    key = args.key
    if key is None:
        key = "1" if cipher == "caesar" else "LEMON"
    if cipher == "caesar":
        key = int(key) if key.isdigit() else 1
    return cipher, key


def freq_count(args):
    _input = _get_input_and_ready_output(args)
    _output = args.output if args.output else 'frequencies.txt'
    _dump_frequencies(_frequencies(_input), _output)


def hack(args):
    _input = _get_input_and_ready_output(args)
    _freqs = _load_frequencies(args.freqs) if args.freqs else _load_frequencies()
    print(caesar_hack(_input, _freqs), end='')


def parse_args():
    parser = argparse.ArgumentParser(description='Encryption utility')
    subparsers = parser.add_subparsers()
    parser_encode = subparsers.add_parser('encode')
    parser_encode.add_argument('--input', type=str, help="text to encode")
    parser_encode.add_argument('--output', type=str, help="where to put encoded text")
    parser_encode.add_argument('--cipher', type=str, help="cipher used to encode text")
    parser_encode.add_argument('--key', help="key to encode text with")
    parser_encode.set_defaults(func=_encode)
    parser_decode = subparsers.add_parser('decode')
    parser_decode.add_argument('--input', type=str, help="text to decode")
    parser_decode.add_argument('--output', type=str, help="where to put decoded text")
    parser_decode.add_argument('--cipher', type=str, help="cipher used to encode text")
    parser_decode.add_argument('--key', help="key used to encode text")
    parser_decode.set_defaults(func=_decode)
    parser_freq = subparsers.add_parser('freq_count')
    parser_freq.add_argument('--input', type=str, help="text to count frequency of letters")
    parser_freq.add_argument('--output', help="where to put list of frequencies")
    parser_freq.set_defaults(func=freq_count)
    parser_hack = subparsers.add_parser('hack_caesar')
    parser_hack.add_argument('--input', type=str, help="file trying to hack")
    parser_hack.add_argument('--output', type=str, help="where to put decoded text")
    parser_hack.add_argument('--freqs', type=str, help="file with serialized dictionary of frequencies")
    parser_hack.set_defaults(func=hack)
    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


main()