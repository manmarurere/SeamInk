# SeamInk

**Tattoo baker for FFXIV skin textures.** Place a transparent PNG on a 3D body and SeamInk writes it into the right spots of your skin texture, seamlessly across UV seams.

[日本語の説明はこちら](#日本語)

Skin textures lay the body out in separate pieces (left and right, upper and lower body, and so on). A design that crosses a seam, such as one around the navel or down the middle of the back, normally has to be cut up and lined up piece by piece in an image editor. SeamInk works backwards from the 3D body instead, so the design stays continuous no matter how the texture is split.

## Features

- Reads your Penumbra settings and loads the body model and skin texture you currently use in game. Pick your race and gender; it shows which file came from which mod.
- Drag to place tattoos on the 3D body. Size, rotation, opacity, mirroring, solid-color recoloring, several layers, mirror copies.
- Pads color past the UV seams so no seam lines appear in game.
- Exports a game-ready `.tex` (uncompressed B8G8R8A8 with mipmaps), a PNG, or the tattoo alone as a transparent PNG. Pixels without a tattoo stay exactly as they were.
- Save a layout and continue later.
- Japanese / English interface.

## Download

Get the latest zip from **[Releases](../../releases)**, extract it, and double-click `Start_SeamInk.bat`.
Full instructions are in [README_en.txt](README_en.txt).

## Requirements

- Windows 10 / 11, Chrome or Edge
- XIVLauncher (Dalamud) and Penumbra
- A modded body and skin (Bibo+ / RueXB / YAB+ / X-Body Skin and similar). Vanilla bodies and skin are not supported.
- [Python](https://www.python.org/downloads/) 3.8 or later (tick "Add python.exe to PATH" when installing)
- An internet connection when it starts (it loads the three.js 3D library)

## How it works

`Start_SeamInk.bat` runs `seamink_server.py`, a small local server on `127.0.0.1` that **only reads**:

1. Penumbra's settings: the mod folder, the collection your character uses, and which mods and options are enabled.
2. The files Penumbra would use for the body: the upper/lower body model (`.mdl`), its skin material (`.mtrl`) for your race, and the diffuse texture that material points to (`.tex`).

The page (`seamink.html`) projects each tattoo from 3D into UV space on the GPU, so every texel gets the ink that belongs to its spot on the body.

It never writes to your Penumbra settings or mod folder, never sends anything off your PC, and serves only `.mdl` / `.mtrl` / `.tex` / `.png` files from inside the Penumbra mod folder.

## Tested with

- Body: RueXB+ (with YAB+ materials). Skin: X-Body Skin Framework [4K] and the skins bundled with RueXB+.
- Because it follows model → material → texture through Penumbra's own settings, it is built to work with other body and skin mods too, but not every mod has been tested.

## Credits

- [three.js](https://threejs.org/) (MIT License)
- Fonts: Zen Kaku Gothic New, IBM Plex Mono (SIL Open Font License)

## License

[MIT](LICENSE)

---

## 日本語

**FF14 の肌テクスチャ用タトゥー転写ツール**です。3D の体の上に透過 PNG を貼ると、UV の継ぎ目をまたいで肌テクスチャの正しい場所へ書き込みます。

肌テクスチャは、体が「左右」「上半身と下半身」などいくつかの部品に分かれて並んでいます。おへそ周りや背中の中心のように継ぎ目をまたぐ柄は、画像編集ソフトでは部品ごとに分けて描く必要がありました。SeamInk は 3D の体から逆算して書き込むので、テクスチャ上でどう分かれていても柄はつながったままになります。

### できること

- Penumbra の設定を読んで、今ゲームで使っている体のモデルと肌テクスチャを自動で読み込み（種族と性別を選ぶだけ。どの mod のどのファイルかも表示）
- 3D の体の上でドラッグして配置。サイズ・回転・濃さ・左右反転・単色化、複数レイヤー、左右対称コピー
- 継ぎ目の外側まで色を広げて、ゲーム内でつなぎ目の線が出ないように処理
- 書き出し：ゲームでそのまま使える `.tex`（無圧縮・ミップマップ付き）／ PNG ／ タトゥーだけの透過 PNG。タトゥーのない部分は元のまま
- 配置の保存・読み込み
- 日本語 / English 切り替え

### ダウンロード

**[Releases](../../releases)** から最新の zip をダウンロードして展開し、`Start_SeamInk.bat` をダブルクリックしてください。
くわしい使い方は [README_ja.txt](README_ja.txt) にあります。

### 必要なもの

- Windows 10 / 11、Chrome または Edge
- XIVLauncher（Dalamud）と Penumbra
- 体と肌を mod で入れていること（バニラの体・肌には対応していません）
- [Python](https://www.python.org/downloads/) 3.8 以上（インストール時に「Add python.exe to PATH」にチェック）
- 起動時のインターネット接続（3D 表示用の three.js を読み込みます）

### 安全について

読み取り専用です。Penumbra の設定や mod のファイルを書き換えることはなく、通信は自分の PC の中（127.0.0.1）だけです。読むのは Penumbra の設定と、mod フォルダ内の `.mdl` / `.mtrl` / `.tex` / `.png` だけです。

### ライセンス

[MIT](LICENSE)
