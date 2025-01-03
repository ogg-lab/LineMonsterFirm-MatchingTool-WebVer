"""
   Copyright 2024/6/29 sean of copyright owner

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

	端的に言えば、改変/二次配布は自由ですが、一切責任は負いません！
	配布時は、必ず"sean"の名前と上記文章をコピーして渡すように！って感じです！
	(改変時は面倒ではありますが変更履歴/内容も記載してください。)

"""

# streamlit関連
import streamlit as st

# 外部ライブラリ
# import psutil
# from memory_profiler import profile

# 自作ライブラリ等
from lib.arrange_widget import init_page_setting



def main():

    init_page_setting("S Tool", "S Tool", "")
    st.subheader("- リリースノート -")
    """
    &nbsp;
    """

    """
    - **2024/05/02：Version 1.1.0**  
      Windows版相性計算ツールをリリース。(現在公開停止中。)  

      
    - **2024/05/19：Version 2.0.1**  
      Windows版相性計算ツールの不具合等を修正。(ダウンロードは[こちら](https://github.com/sean-sheep1/LineMonsterFirm-MatchingTool-LocalVer ""))  
      ただし、更新停止中。  
    
      
    - **2024/06/02：Version 3.0.0**  
      Windows版相性計算ツールをWebアプリ化。  
      (★注意)キジン種については未対応。  

      
    - **2024/06/16：Version 3.1.0**  
      * 各ページの誤記を修正  
      * オーディーン追加  
      * Z-ABB×BAA等のパターン検索に対応（詳細は補足ページやマニュアルページを参照。）  
      * パターン検索時限定で、子の血統指定検索に対応（詳細はヘルプページを参照。）  
      * 全パターン検索時の閾値自動修正機能無効化ボタンの追加  
      * "補足ページ"に、秘伝と相性に関連する基本的な説明を追加  
      （初心者の方はこちらを一読することで理解が深まると思われます。）  

      
    - **2024/06/23：Version 3.2.0**  
      * パターン検索のバリエーションを追加（詳細は補足ページやマニュアルページを参照。）  
      * 検索結果を利用した逆引き検索機能の追加（詳細はマニュアルページを参照。）  
      * 共通秘伝による相性値の加算ができる機能を追加（詳細は補足ページやマニュアルページを参照。）
      * 検索除外モンスター指定機能の追加（詳細はマニュアルページを参照。）
      * 試験的に、自動検索モード追加（詳細はマニュアルページを参照。）  
        なお、自動検索モード使用時は必ずマニュアルページをご確認ください。（サーバーが落ちる原因となりえます。）  
      * 全パターン検索時の仕様を一部変更。  
      * 一部レイアウトやラベル名の調整  
      * 一部操作上のバグ等を修正。  
      * 上記修正や機能追加に合わせた各ページの記載修正/追加。  
    
      .
      
    - **2024/06/24：Version 3.2.1**  
      * 各種バグや誤記の修正  

      .

      
    - **2024/06/30：Version 3.3.0**  
      * 選択リストの並び順を変更。  
      * モンスター参照テーブルにて、両親祖父母に、レアモン、純血統のみを使うテーブルを追加。  
      * 「出力パターン」の「選択パターン」で4,5,6の出力内容をどちらか一方から両方に変更。  
      * 逆引き検索時に処理時間がかかってしまう件の微改善。  
      * 逆引き検索時に、相性がよさそうな種族候補を出力。(出力結果の見方は必ずマニュアルの内容を一読のこと。)  
      * 逆引き検索時に、逆親検索結果も出力。  
      * 逆引き検索結果で、基本統計量情報などを出力。  
      * 逆引き検索結果の相性値に関するヒストグラムを表示する機能を追加。  
      * 一部バグの修正。  
      * アンタレス、ヨロイモッチーの追加。(以降、新モンスターの追加は新血統を除いて記載しない。)  
      * 上記修正等に合わせて、各ページを更新。  

      なお、現状特に不都合がないため、ハクタク等、一部名称変更されたモンスターへの名称変更適用は未実施としている。   



    - **2024/12/9：Version 3.4.0**  
      * "詳細設定"に"検索モード"を追加し、従来検索方法に加えて、子を複数指定して汎用的な検索ができるように対応。  
        （詳細は"マニュアル"ページの"検索モード"の項目を参照。）

      .
        

    - **2024/12/22：Version 3.5.0**  
      * "検索モード"を"子のみ指定汎用検索モード"をデフォルト設定に変更。  
      * "検索モード"を"子のみ指定汎用検索モード"指定時でも"検索除外モンスター指定"を利用可能に変更。  
      * "子のみ指定汎用検索モード"使用時の"逆引き検索結果一覧"を純血統のみ出力するように変更。(親がレアモンの場合、同種族の相性値は同じとなるため。)  
      * キジン種追加（有識者より情報提供いただきました。ありがとうございます。）  

      .

      
    - **2024/12/23：Version 3.6.0**  
      * メタルナー種追加（有識者より情報提供いただきました。ありがとうございます。★ただし、検証中の値のため注意。）  


    """



# 呼び出し
if __name__ == '__main__':
    main()


