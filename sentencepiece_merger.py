from sentencepiece_model_pb2 import ModelProto

import argparse
import math
import numpy as np
from scipy.special import logsumexp
import regex as re
from langdetect import detect


NORMALIZE_BASE = False


def merge_models(base_model_path, target_model_path, config):
    base = load_model(base_model_path)
    target = load_model(target_model_path)

    "Step0: Show metrics of base and target models"
    show_metrics_of_model(base, "Base")
    show_metrics_of_model(target, "Target")
    if config.output is None:
        return

    print("Step1: Create hash table for base and target models")
    base_hash = create_hash_table(base)
    target_hash = create_hash_table(target)

    print("Step2: Normalize target score to consider noomarize and prioritize factor")
    base_normalize_factor = get_normalize_factor(base)
    target_normalize_factor = get_normalize_factor(target)
    normalize_factor = target_normalize_factor
    if NORMALIZE_BASE:
        normalize_factor -= base_normalize_factor

    for target_sp in target.pieces:
        if config.normalize:
            target_sp.score += normalize_factor
        if config.prioritize:
            target_sp.score -= math.log(config.prioritize)

    print("Step3-1: Merge models - Update existing pieces from target model")
    for sp in base.pieces:
        if sp.piece in target_hash:
            target_sp = target_hash[sp.piece]
            if config.merge_style == 'max':
                sp.score = max(sp.score, target_sp.score)
            elif config.merge_style == 'target':
                sp.score = target_sp.score

    print("Step3-2: Merge models - Add new pieces from target model")
    for sp in target.pieces:
        if sp.piece not in base_hash:
            base.pieces.append(sp)

    print("Step4: Sort the merged model")
    normal_pieces = [sp for sp in base.pieces if sp.type == ModelProto.SentencePiece.NORMAL]
    special_pieces = [sp for sp in base.pieces if sp.type != ModelProto.SentencePiece.NORMAL]
    if config.sort == 'score':
        normal_pieces.sort(key=lambda sp: -sp.score)
    elif config.sort == 'alphabet':
        normal_pieces.sort(key=lambda sp: sp.piece)
    del base.pieces[:]
    base.pieces.extend(special_pieces + normal_pieces)

    print("Step5: Save the merged model")
    save_model(base, config.output)


def load_model(model_path):
    m = ModelProto()
    m.ParseFromString(open(model_path, "rb").read())
    return m


def save_model(model, output_path):
    with open(output_path, "wb") as f:
        f.write(model.SerializeToString())


def create_hash_table(model):
    return {sp.piece: sp for sp in model.pieces}


def extract_middle_score(model):
    scores = sorted([sp.score for sp in model.pieces])
    n = len(scores)
    return scores[n // 2]


def find_unkown_piece(model):
    for sp in model.pieces:
        if sp.type == ModelProto.SentencePiece.UNKNOWN:  # or sp.piece == "<unk>":
            return sp
    return None


english_pattern = re.compile(r'[A-Za-z0-9\s!\"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~▁]+')
japanese_pattern = re.compile(r'[ぁ-んァ-ン一-龯々〆〤▁]+')
symbol_pattern = re.compile(r'[\p{P}\p{Emoji}\p{InCJK_Symbols_and_Punctuation}×−▁]+')


def detect_language(piece):
    if english_pattern.fullmatch(piece):
        return "en"
    elif japanese_pattern.fullmatch(piece):
        return "ja"
    elif symbol_pattern.fullmatch(piece):
        return "symbol"
    else:
        try:
            return detect(piece)
        except Exception:
            return "unknown"


def print_pieces(model):
    for sp in model.pieces:
        print(sp.type, sp.piece, sp.score)


def print_non_english_japanese_pieces(model):
    for sp in model.pieces:
        lang = detect_language(sp.piece)
        if lang != "en" and lang != "ja" and lang != "symbol" and lang != "unknown":
            lang = detect_language(sp.piece)
            print(sp.type, sp.piece, lang, sp.score)


def print_special_pieces(model, exclude_byte=True):
    for sp in model.pieces:
        if sp.type == ModelProto.SentencePiece.NORMAL:
            continue
        if exclude_byte and sp.type == ModelProto.SentencePiece.BYTE:
            continue
        print(sp.type, sp.piece, sp.score)


def get_normalize_factor(model):
    return -calculate_log_total_probability(model)


def calculate_log_total_probability(model):
    scores = np.array([sp.score for sp in model.pieces if sp.type == ModelProto.SentencePiece.NORMAL])
    return logsumexp(scores)


def show_metrics_of_model(model, name: str):
    middle_score = extract_middle_score(model)
    print("-----------------------------------------------")
    print("Model:", name, model.trainer_spec.model_prefix)
    print("Pieces:", len(model.pieces))
    print("Middle score:", middle_score, "probability:", math.exp(middle_score))
    print("Total probability:", math.exp(calculate_log_total_probability(model)))
    print("Special Chars:", math.exp(calculate_log_total_probability(model)))
    print_special_pieces(model)
    print("-----------------------------------------------")


class MergeConfig:
    def __init__(self, output=None, sort='none', merge_style='max', normalize=False, prioritize=None):
        self.output = output
        self.sort = sort
        self.normalize = normalize
        self.merge_style = merge_style
        self.prioritize = prioritize


def main():
    parser = argparse.ArgumentParser(description='Merge two SentencePiece models')
    parser.add_argument('base_model', type=str, help='Path to the base SentencePiece model')
    parser.add_argument('target_model', type=str, help='Path to the target SentencePiece model')
    parser.add_argument('--output', type=str, help='Path to the output SentencePiece model', default=None)
    parser.add_argument('--sort', choices=['score', 'alphabet', 'none'], default='none', help='Sort order for merging')
    parser.add_argument('--merge_style', choices=['max', 'base', 'target'], default='max', help='How the model is merged in case of conflict')
    parser.add_argument('--normalize', action='store_true', help='Apply target score normalization on merging')
    parser.add_argument('--prioritize', type=float, help='Priority multiplier for base model scores', default=None)
    args = parser.parse_args()

    config = MergeConfig(output=args.output, sort=args.sort, merge_style=args.merge_style, normalize=args.normalize, prioritize=args.prioritize)

    merge_models(args.base_model, args.target_model, config)


if __name__ == '__main__':
    main()
