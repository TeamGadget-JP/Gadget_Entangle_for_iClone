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

## 前提条件 ##
1. 公式プラグイン`Unity Pipeline``Unity Auto Setup`を使用することを前提に開発しています。

##  開発の目的そして今後の方針(OSS化)
GEC、GEP、GTransporter、GETL、そして今回のGEiはUnityをベースとした映像制作環境(VP)を個人ベースで実現できないか？というのが最大の開発目的です。
そしてそれを実現することを目標にツールの制作をしています、ですから、その他の用途でご使用される方は意図する動作をしてくれないケースもあるかと思います、
運用方法の工夫などで解決できれば良いのですが、スクリプトを直接いじらないと駄目なこともあるでしょう。そこで今回の公開からはOSSとした次第です。
また、いままでリリーズ済みのツールも開発元ライセンスを遵守しなければならない物以外は今後、順次OSS公開に切り替えていきます。

##  重要な注意事項（必ずお読みください）
* **サポートなし（現状渡し）:** 開発者は普段、別の本業を抱えるFA系個人エンジニアです。そのため、個別の環境に合わせた技術サポートを提供することは事実上不可能です。本ツールは「完全無料・サポート対象外」として提供されます。
* しかしながら、バグフィックスやバージョンアップは不定期ながらも行って行くつもりです、皆様からのフィードバックは大歓迎です。些細なことでもどんどん書き込んで下さると助かります！

##  開発者からのお願い
もし皆様の制作のお役に立てましたら、ぜひ**YouTubeチャンネルの登録と高評価**をお願いいたします
皆様からの応援が、今後の開発の最大のモチベーションになります
▶️ [https://youtu.be/kNBWSCf2cIw](https://www.youtube.com/channel/UCj9OYwzMAIgYAeVkTV4wczw)

---
**Windows専用:** 本ツールは現在、Windows環境でのみ動作します(Windows APIを使用しているため)。macOSやLinuxでは動作しません。

## 導入手順と使用方法

### 1. Cascadeur側の準備
1. このリポジトリから `GEC_TimeReceiver.py` をダウンロードします。
2. CascadeurのPythonプラグインフォルダに配置します：`[Cascadeurインストール先]\resources\scripts\python\commands\`
3. Cascadeurを起動します。
4. `メニューバー > Commands > GETL TimeLine Receiver`をクリック。
5. Event logに`▶️[GETL TimeLine Receiver]Started syncing with Unity!(Port:8991)`を表示されば同期準備OKです。
6. もう一度`メニューバー > Commands > GETL TimeLine Receiver`をクリックして同期停止です。

### 2. iClone側の準備
1. このリポジトリから `GEi_TimeReceiver.py` をダウンロードします。
2. iCloneを起動します。
3. `メニューバー > Script > Load Python`をクリック。
4. 1.でダウンロードした`GEi_TimeReceiver.py`を読込。
5. ダイアログが開きますので`▶ START SYNC(Port:8992)`ボタンで同期開始。

### 3. Unity側の準備と使用方法
1. このリポジトリから `GETL_v1.0.0.unitypackage` をダウンロードします。
2. Unityプロジェクトにインポートします（`Assets > Import Package > Custom Package...`）。
3. Project > Assets > Gadget > Editor に`GETL_Recorder.cs`が入ります。
4. Project > Assets > Gadget > Scripts に`GETL_Broadcaster.cs`が入ります。
5. Hierarchy に空のゲームオブジェクトを制作します、名称は任意です、それに`GETL_Broadcaster.cs`をアタッチしてください。
6. 5.の空のゲームオブジェクト(名前をつけていればそれに)を選択して`Window > Sequencing > Timeline`
7. Timelineウィンドウの`Create > 任意の名前で作成`これでシークバーを動かせば同期します。

### 4. アニメーションベイクの仕方
1. ツールバー`Gadget > GETL Recorder`でGETL Recorder UIが開きます。
2. Target Avatar にアニメーションベイクしたいキャラクターをドラッグアンドドロップ。
3. Playable Director に GETL_Broadcaster.csをアタッチしたゲームオブジェクトをドラッグアンドドロップ。
4. Overwrite Clip に `.anim`をドラッグアンドドロップ。
5. Target Frame Rate は Cascadeur や iClone で30だったり60だったりしますので、合わせて設定してください。
6. GETL_Broadcaster.csをアタッチしたゲームオブジェクトのInspector にも Target Frame Rate 項目がありますので忘れずにそちらも合わせてください。
7. `Bake Delay(sec)`はそのままでいいと思います。
8. iClone を同期してベイクする場合は`Bake Facial(Blendshape)`チェックを入れて下さい。
9. 後は`●START ANIMATION BAKE`ボタンを押すだけでベイクします。

## ⚠️ 重要事項：Unityのタイムライン仕様とHumanoid Avatarに関する制限 ##
GECやGEiは、従来のFBXファイルを経由するワークフローとは異なり、スクリプトを通じて直接ボーン情報を取得し、Unity上のキャラクターに適用しています。
リアルタイム同期の実行中は、スクリプトがキャラクターの `Humanoid Avatar` の制御を無視し、強制的にボーンのトランスフォームを上書きすることで同期を実現しています。
しかし、ベイクしたアニメーションを**Unity公式のタイムラインで再生する際**には、この `Humanoid Avatar` の影響を回避することができません。
そのため、`Humanoid Avatar` が適用されたままの状態でタイムラインを再生すると、キャラクターのメッシュが無惨に潰れたり、姿勢が破綻してしまいます。
これを回避する唯一の方法は、**キャラクターのAnimatorから `Avatar` を外す（Noneにする）こと**です。
映像制作（VP）目的であればこの運用で全く問題ありませんが、アニメーションの流用やステートマシンの利用が必須となる**ゲーム制作においては致命的な問題**となります。
したがって、最終的な目的がゲーム開発である場合、本ツールを使用したアニメーションのベイクは推奨しません。あくまで「映像制作向けの機能」としてご活用ください。

---
本ソフトウェアは独自ライセンスのもとで提供されています。改変は可としますが、販売等の目的での無断再配布は固く禁じられています。
詳細については、[LICENSE](./LICENSE) ファイルをご確認ください。
