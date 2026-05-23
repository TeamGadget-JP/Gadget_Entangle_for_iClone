# Gadget Entangle for iClone (GEi)

## Core Features of GEi ##
1. Establishes a real-time connection between Reallusion's character animation software `iClone 8` and Unity, enabling live pre-visualization (Live Previz).
2. Supports simultaneous synchronization of multiple characters (by assigning a dedicated port to each character).
3. Supports a "Hybrid Mode" that combines body animation from Cascadeur with facial animation from iClone.

## Supported & Unsupported Features (Current Status) ##
1. Does not fully support all of iClone's Motion features. However, features like `Edit Motion Layer` and `AccuPOSE` synchronize without any issues.
2. Major iClone Facial features (`Create Script`, `Face Puppet`, `Face Key`) should be well supported. (Since I am not completely familiar with every single feature, there might be some minor unexpected behaviors).
3. When applying and playing back pre-made animations (motions) from the content library, there is a known issue where the character's hip gets fixed in world space, causing the character to slide. Although I managed to solve this in a previous showcase video, it resurfaced during recent development. As I haven't found a complete breakthrough yet, this issue is currently put on hold for this version.
4. "Motion Director" has not worked properly since the early stages of development and is currently on hold.
5. You may encounter various other issues as you use it, but since manual keyframe animation (hand-keyed animation) works without noticeable problems at this stage, I decided to release it as is.
6. Not all character generations have been tested. Operation has been confirmed with the current latest CC5HD and CC3+ characters.

## Prerequisites ##
1. Developed with the assumption that the official Reallusion plugins `Unity Pipeline` and `Unity Auto Setup` are installed and used.
2. Assumes a workflow of character setup in Character Creator 5 (CC5) and animation creation in iClone 8.

## Development Purpose and Future Direction (Open Source)
The ultimate goal of developing GEC, GEP, GTransporter, GETL, and now GEi is to realize a personal-scale Virtual Production (VP) environment based on Unity.
These tools are built specifically to achieve that goal. Therefore, if you use them for other purposes, they might not behave as intended. While creative workflows might solve some issues, there will be cases where you need to modify the scripts directly. 
For this reason, I have decided to make this release Open Source (OSS). Furthermore, previously released tools will also be transitioned to open source gradually, except for those that must comply with original developer licenses.

## ⚠️ Important Notices (Please Read)
* **No Support (As-is Delivery):** The developer is a personal FA (Factory Automation) engineer with a full-time day job. Therefore, it is practically impossible to provide individual technical support tailored to specific environments. This tool is provided "Completely Free / No Support".
* However, I do plan to provide bug fixes and version updates irregularly. Feedback from everyone is highly welcome! Even the smallest details are helpful, so please don't hesitate to post them.

## A Request from the Developer
If this tool helps your production, I would be thrilled if you could **Subscribe to my YouTube channel and leave a Like!**
Your support is the greatest motivation for my future development!
▶️ [https://youtu.be/kNBWSCf2cIw](https://www.youtube.com/channel/UCj9OYwzMAIgYAeVkTV4wczw)

Also, regardless of language, please feel free to leave any comments, feedback, or strict evaluations about your experience using the tool. It will greatly help future development!

---
**Windows Only:** This tool currently runs only on Windows environments (as it uses the Windows API). It does not work on macOS or Linux.

## Installation and Usage

### 1. iClone Setup
1. Download `GEi_Transmitter.py` from this repository.
2. Launch iClone.
3. From the top menu, go to `Script > Load Python` and select the `GEi_Transmitter.py` file.
4. The GEi Transmitter UI will open.
5. In the "Target Character (Link ID & Port)" section, paste the character's ID (You can check this via Unity Data Link or the Data Link Actor Data component in Unity).
6. Set any desired Port number for each character.
7. Check the box if you want to use `Hybrid Mode`.
8. Click the `START STREAM` button to prepare for synchronization.

### 2. Unity Setup
1. Download `GEi_v1.0.0.unitypackage` from this repository.
2. Import it into your Unity project (`Assets > Import Package > Custom Package...`).
3. The script `GEi_Receiver.cs` will be placed in `Project > Assets > Gadget > Scripts`.
4. Drag and drop `GEi_Receiver.cs` onto your target character in the Hierarchy to attach it.
5. In the Inspector, enter the corresponding port number in `Listen Port`, and drag and drop the character from the Hierarchy into the `Target Character` slot.
6. Leave other parameters as they are, check the `Is Listening` box, and the synchronization will start.

### 3. Hybrid Mode Setup
1. In the Inspector for `GEC_Bone Entangler`, leave the `Neck` and `Head` fields empty. This prevents the character from receiving bone data above the neck from Cascadeur.
2. Turn on `Hybrid Mode` in the GEi UI panel on the iClone side and connect. You are all set!

---
## 日本語 ##
# Gadget Entangle for iClone (GEi)

## GEiの主要機能 ##
1. Reallusion製キャラクターアニメーションソフト`iClone8`とUnityをリアルタイムで接続してライブ・プレビズを実現することが可能です。
2. 複数のキャラクターの同時同期に対応(キャラクター毎にポートを割り当てる方式)
3. Cascadeur(ボディーアニメーション)とiClone(フェイシャルアニメーション)のハイブリッド化対応。

## 対応・未対応の状況 ##
1. iCloneのMotion機能の全てにフル対応はできていません。`Edit Motion Layer`や`AccuPOSE`等は問題無く同期します。
2. iCloneのFacial機能`Create Script`、`Face Puppet`、`Face Key`の主要機能には多分対応できていると思いますが(全ての機能に精通しているわけではないので細かな部分であれ？はあるかも知れません)
3. コンテンツにあるアニメーション(モーション)をキャラクターに適用して再生した時に腰が空間に固定されて滑る現象があります。以前の紹介動画では解決できていたのですが、その後の開発を進める中で再発してしまい、解決の糸口が見つからないのでこのバージョンでは保留としました。
4. モーション・ディレクターは当初から上手くいかず、これも保留としました。
5. その他、使用していく中で色々問題は出るかと思いますがひとまず現段階で手付けアニメーションであれば問題は見られないので公開に踏み切りました。
6. 全ての世代のキャラクターの動作確認はしていません。現行最新のCC5HD、CC3+のキャラクターの動作確認は取れています。

## 前提条件 ##
1. 公式プラグイン`Unity Pipeline``Unity Auto Setup`を使用することを前提に開発しています。
2. CC5でキャラクターセットアップ、iClone8でアニメーション作成を前提としています。

##  開発の目的そして今後の方針(OSS化)
GEC、GEP、GTransporter、GETL、そして今回のGEiはUnityをベースとした映像制作環境(VP)を個人ベースで実現できないか？というのが最大の開発目的です。
そしてそれを実現することを目標にツールの制作をしています、ですから、その他の用途でご使用される方は意図する動作をしてくれないケースもあるかと思います、
運用方法の工夫などで解決できれば良いのですが、スクリプトを直接いじらないと駄目なこともあるでしょう。そこで今回の公開からはOSSとした次第です。
また、いままでリリーズ済みのツールも開発元ライセンスを遵守しなければならない物以外は今後、順次OSS公開に切り替えていきます。

##  ⚠️ 重要な注意事項（必ずお読みください）
* **サポートなし（現状渡し）:** 開発者は普段、別の本業を抱えるFA系個人エンジニアです。そのため、個別の環境に合わせた技術サポートを提供することは事実上不可能です。本ツールは「完全無料・サポート対象外」として提供されます。
* しかしながら、バグフィックスやバージョンアップは不定期ながらも行って行くつもりです、皆様からのフィードバックは大歓迎です。些細なことでもどんどん書き込んで下さると助かります！

##  開発者からのお願い
もし皆様の制作のお役に立てましたら、ぜひ**YouTubeチャンネルの登録と高評価**をお願いいたします
皆様からの応援が、今後の開発の最大のモチベーションになります
▶️ [https://youtu.be/kNBWSCf2cIw](https://www.youtube.com/channel/UCj9OYwzMAIgYAeVkTV4wczw)

また、言語問わずツールの使用感や厳しい評価など、何でも構いませんので意見や感想等をお気軽に書き込みお願いします！
今後の開発に大いに役立ちます。

---
**Windows専用:** 本ツールは現在、Windows環境でのみ動作します(Windows APIを使用しているため)。macOSやLinuxでは動作しません。

## 導入手順と使用方法

### 1. iClone側の準備
1. このリポジトリから `GEi_Transmitter.py` をダウンロードします。
2. iCloneを起動します。
3. ツールバーから`Script > Load Python > ファイル"GEi_Transmitter.py"を選択`
4. GEi Transmitter UIが開きます。
5. Target Character(Link ID Port)項目にキャラクターのID(Unity Data LinkやUnity側のData Link Actor Dataコンポーネントで確認できます)をコピペする。
6. Portは任意に決めてください。
7. Hybrid Modeを使用する場合はチェックを入れる。
8. `START STREAM`ボタンで同期準備完了です。

### 2. Unity側の準備
1. このリポジトリから `GEi_v1.0.0.unitypackage` をダウンロードします。
2. Unityプロジェクトにインポートします（`Assets > Import Package > Custom Package...`）。
3. Project > Assets > Gadget > Scripts に`GEi_Receiver.cs`が入ります。
4. Hierarchyに居るキャラクターに`GEi_Receiver.cs`をドラッグアンドドロップしてアタッチする。
5. Inspectorの`Listen Port`に対応するポート番号を入力、Target CharacterにHierarchyのキャラクターをドラッグアンドドロップ。
6. パラメーターはそのままで、`is Listening`にチェックを入れれば同期スタートします。

### 3. ハイブリッドの準備
1. GEC_Bone EntanglerのInspectorで`Neck`と`Head`の2項目を空にしてください。これによってCascadeurから首より上のボーン情報を受け付けないようにします。
2. iClone側のUIパネルで`Hybrid Mode`をオンにして接続すれば完了です。

---
本ソフトウェアは独自ライセンスのもとで提供されています。改変は可としますが、販売等の目的での無断再配布等は固く禁じられています。
詳細については、[LICENSE](./LICENSE) ファイルをご確認ください。
