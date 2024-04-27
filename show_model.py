from sentencepiece_merger import load_model, show_metrics_of_model, print_pieces, print_non_english_japanese_pieces

import argparse


def show_model(model_path, only_foreign=False):
    model = load_model(model_path)
    if only_foreign:
        print_non_english_japanese_pieces(model)
        return
    show_metrics_of_model(model, model_path)
    print_pieces(model)


def main():
    parser = argparse.ArgumentParser(description='show SentencePiece model')
    parser.add_argument('model', type=str, help='Path to the SentencePiece model')
    parser.add_argument('--only-foreign', action='store_true', default=False, help='Show only foreign(not english/japanese) pieces')
    args = parser.parse_args()
    show_model(args.model, args.only_foreign)


if __name__ == '__main__':
    main()
