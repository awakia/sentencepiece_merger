# sentencepiece_merger

SentencePieceで作られた2つのの.modelファイルを統合するためのツールです。
マージプロセスでは、基本モデルとターゲットモデルの両方からトークンを組み合わせ、新しいモデルを作成します。

## 使い方

準備として、Poetryにより必要な依存ライブラリをインストールします。

```
poetry install
```

メインのコマンドは以下のように使います。

```
poetry run python sentencepiece_merger.py <base_model_path> <target_model_path> [オプション]
```

- `<base_model_path>`: ベースとなるSentencePieceモデルのパス。
- `<target_model_path>`: マージしたいターゲットのSentencePieceモデルのパス。

### オプション

- `--output <output_model_path>`: マージ後のモデルを保存するパス。指定しない場合、結果は保存されません。
- `--sort {score, alphabet, none}`: マージ後のトークンのソート順。スコアに基づくソート、アルファベット順、またはソートなしを選択できます。デフォルトは `none` です。
- `--merge_style {max, base, target}`: トークンが両方のモデルに存在する場合のマージスタイル。`max` を選択すると、スコアが最大のトークンが選択されます。`base` または `target` を選択すると、それぞれのモデルのトークンスコアが使用されます。デフォルトは `max` です。
- `--normalize`: このオプションを指定すると、ターゲットモデルのスコアを正規化してマージします。
- `--prioritize <float>`: ベースモデルのスコアに優先度を乗算します。デフォルトは指定なしです。

### 例

基本モデル `base.model` とターゲットモデル `target.model` をマージし、結果を `merged.model` に保存する例は以下の通りです。

```
poetry run python sentencepiece_merger.py base.model target.model --output merged.model --sort score --merge_style max --normalize --prioritize 1.5
```

このコマンドは、スコアに基づいてトークンをソートし、トークンの衝突がある場合はスコアが最大のものを選択し、ターゲットモデルのスコアを正規化し、ベースモデルの方が1.5倍ほとターゲットモデルよりも出現しやすかった前提でマージします。

### 推奨の使用例

```
poetry run python sentencepiece_merger.py data/base.model data/target.model --output=data/merged.model --sort=alphabet --normalize
```


## 基本アイデア

- [Manually modifying SentencePiece model? · Issue \#121 · google/sentencepiece](https://github.com/google/sentencepiece/issues/121)に、sentencepieceのモデルを開いて単語を追加する方法が書いてある
- これをもとに、二つも.modelファイルの統合を試みる
- 元々sentencepieceのpiecesに入っているscoreは出現確率Pの対数をとったものlog(P)である
- これをもとに元々の出現確率などがほぼ計算できるので、複数のモデルをマージすることができる
- 混ぜる時にbaseに比べてtargetがどのくらいの頻度で現れるかの事前知識を入れると結果も変わるのでそこら辺の話をオプションで調整できるようにしている。


## ファイルの説明

- sentencepiece_merger.py
  - メインのファイル
- sentencepiece_model_pb2.py
  - https://github.com/google/sentencepiece/blob/master/python/src/sentencepiece/sentencepiece_model_pb2.py より
  - 参考: [sentencepiece_model.proto](https://github.com/google/sentencepiece/blob/master/src/sentencepiece_model.proto)
- show_model.py
  - `python run show_model.py target.model` というコマンドでmodelの中身を表示する
- pyproject.toml
  - poetryの設定ファイル
- pyproject.toml
  - poetryのLockファイル

### data

- data/botchan.model
  - 坊ちゃん英語版のデータより生成
- data/llm-jp-tokenizer-100k.ver3.0b1.model
  - https://github.com/llm-jp/llm-jp-tokenizer/blob/main/models/ver3.0/llm-jp-tokenizer-100k.ver3.0b1.model より

