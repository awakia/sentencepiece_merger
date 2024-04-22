from sentencepiece_merger import load_model, show_metrics_of_model, print_pieces

import argparse


def show_model(model_path):
    model = load_model(model_path)
    show_metrics_of_model(model, model_path)
    print_pieces(model)


def main():
    parser = argparse.ArgumentParser(description='show SentencePiece model')
    parser.add_argument('model', type=str, help='Path to the SentencePiece model')
    args = parser.parse_args()
    show_model(args.model)


if __name__ == '__main__':
    main()
