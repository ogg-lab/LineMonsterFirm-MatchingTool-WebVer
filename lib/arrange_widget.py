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
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

# 外部ライブラリ
import pandas as pd
# import psutil
# from memory_profiler import profile
import matplotlib.pyplot as plt
import japanize_matplotlib

# 標準ライブラリ
# import copy
# import time

# 自作ライブラリ等
from lib.classes import DataList
from lib.classes import SessionDataList
from lib.process_event import entry_set_th
from lib.process_event import radio_disable_entry_cmb
from lib.process_event import entry_set_th_from_cmb
from lib.process_event import select_set_ops
from lib.process_event import reset_select_box
from lib.process_event import button_calc_affinity
from lib.process_event import select_calc_affinity 
from lib.process_log import print_log



# ページの初期設定
def init_page_setting(web_title, title, version):

    # ページ設定
    st.set_page_config(page_title=web_title, layout="wide", initial_sidebar_state="expanded")

    # 見出しのリンクを削除
    delete_link()

    # タイトル
    st.title(title)
    st.write(version)

    return



def delete_link():

    # 見出しについてしまうリンクを削除
    st.html(
        body="""
            <style>
                /* hide hyperlink anchors generated next to headers */
                h1 > div > a {
                    display: none !important;
                }
                h2 > div > a {
                    display: none !important;
                }
                h3 > div > a {
                    display: none !important;
                }
                h4 > div > a {
                    display: none !important;
                }
                h5 > div > a {
                    display: none !important;
                }
                h6 > div > a {
                    display: none !important;
                }
            </style>
        """,
    )

    return



# セッション系の初期化
def init_session_state(datalist):

    # 個別保存領域の初期化
    if "session_datalist" not in st.session_state:
        st.session_state.session_datalist = SessionDataList()
        # セレクトボックスの絞込み用のDataFrame型を用意。
        st.session_state.session_datalist.df_monsters_c = datalist.df_monsters
        st.session_state.session_datalist.df_monsters_pg = datalist.df_monsters
        # 補足ページに出力するための
        st.session_state.session_datalist.df_affinities_m_cp = datalist.df_affinities_m_cp
        st.session_state.session_datalist.df_affinities_s_cp = datalist.df_affinities_s_cp

    # セレクトボックス選択結果保存域作成
    for i in range(DataList.num_monster):
        if f"select_ops_name{i}" not in st.session_state:
            st.session_state[f"select_ops_name{i}"] = ""
        elif f"select_ops_main{i}" not in st.session_state:
            st.session_state[f"select_ops_main{i}"] = ""
        elif f"select_ops_sub{i}" not in st.session_state:
            st.session_state[f"select_ops_sub{i}"] = ""

    # 全セレクトボックスの初期リスト設定
    if "select_options" not in st.session_state:
        st.session_state.select_options = [ [ 0 for j in range(DataList.num_monster) ] for i in range(DataList.num_kind)]
        for i in range(DataList.num_monster):
            st.session_state.select_options[0][i] = datalist.lis_mons_names
            st.session_state.select_options[1][i] = datalist.lis_main_ped
            st.session_state.select_options[2][i] = datalist.lis_sub_ped

    # 自動検索モード
    if f"auto_search_mode" not in st.session_state:
        st.session_state.auto_search_mode = False
    
    # 検索モード
    if "radio_search_mode_list" not in st.session_state:
        st.session_state.radio_search_mode_list = ["1.任意指定通常検索モード", "2.子のみ指定汎用検索モード"]
    
    if "radio_search_mode" not in st.session_state:
        st.session_state.radio_search_mode = st.session_state.radio_search_mode_list[1]
    
    # 検索対象モンスター保存場所
    if "search_mons_list" not in st.session_state:
        st.session_state.search_mons_list = []

    # 共通秘伝
    if "input_common_aff2" not in st.session_state:
        st.session_state.input_common_aff2 = 0
    if "input_common_aff3" not in st.session_state:
        st.session_state.input_common_aff3 = 0

    ### ラジオボタンの選択結果保存領域作成(★ラジオボタンの選択結果は先頭1文字を使用して判別しているため注意。)
    # 参照テーブル設定
    if "radio_table_list" not in st.session_state:
        st.session_state.radio_table_list = ["1.純血統+レア", "2.全モンスター", "3.全モンスター(純血統のみ除く)", "4.純血統のみ", "5.レアモンのみ"]

    if "radio_c" not in st.session_state:
        st.session_state.radio_c = st.session_state.radio_table_list[1]
    if "radio_pg" not in st.session_state:
        st.session_state.radio_pg = st.session_state.radio_table_list[1]
    if "radio_c_prev" not in st.session_state:
        st.session_state.radio_c_prev = st.session_state.radio_table_list[1]
    if "radio_pg_prev" not in st.session_state:
        st.session_state.radio_pg_prev = st.session_state.radio_table_list[1]

    # 削除対象モンスター保存場所
    if "del_mons_list" not in st.session_state:
        st.session_state.del_mons_list = []
    
    # 計算式設定
    if "radio_calc_list" not in st.session_state:
        st.session_state.radio_calc_list = ["1.min(m)式", "2.min(m+s)式"]
    
    if "radio_calc" not in st.session_state:
        st.session_state.radio_calc = st.session_state.radio_calc_list[1]
    
    # 出力パターン設定
    if "radio_ptn_list" not in st.session_state:
        st.session_state.radio_ptn_list = ["1.全パターン", "2.特定パターン"]
    
    if "radio_ptn" not in st.session_state:
        st.session_state.radio_ptn = st.session_state.radio_ptn_list[1]

    # 出力パターンのチェックボックス設定内容保存場所
    for i in range(DataList.num_check_ptn):
        if f"check_ptn{i}" not in st.session_state:
            st.session_state[f"check_ptn{i}"] = True

    # セレクトボックスの有効/無効化フラグ(出力パターンに依存)
    if f"select_ops_disabled" not in st.session_state:
        st.session_state.select_ops_disabled = [False] * DataList.num_monster
        st.session_state.select_ops_disabled[3] = True
        st.session_state.select_ops_disabled[5] = True
        st.session_state.select_ops_disabled[6] = True 
    
    # 出力パターンのチェックボックス有効無効化フラグ
    if f"check_ptn_disabled" not in st.session_state:
        st.session_state.check_ptn_disabled = False

    # 閾値設定の自動切換えの有効/無効化フラグ
    if f"input_threshs_chg_disabled" not in st.session_state:
        st.session_state.input_threshs_chg_disabled = False

    # 閾値関連の領域初期化
    for i in range(DataList.num_threshs):
        if f"input_thresh{i}" not in st.session_state:
            st.session_state[f"input_thresh{i}"] = 0
    if f"input_thresh" not in st.session_state:
       st.session_state.input_thresh = True
       entry_set_th()

    # 閾値設定箇所の有効/無効化フラグ
    if f"input_threshs_disabled" not in st.session_state:
        st.session_state.input_threshs_disabled = [True] * DataList.num_threshs

    # 1回以上検索しているかどうかのフラグ
    if f"is_search_once_more" not in st.session_state:
        st.session_state.is_search_once_more = False

    return



# リセット/セレクトボックスの作成
def create_select_area(datalist):

    # 表示
    st.write('')
    st.header('◾モンスター名設定', help="ここで検索したいモンスターの設定をします。全て空白でも検索可能です。(メイン/サブ血統欄は、基本的にモンスター名絞込み用の設定です。）")

    if int(st.session_state.radio_search_mode[0]) != 2:
        # リセットボタンの作成(押下でリセット＆セレクトボックス作成)
        if st.button('モンスター名選択リセット', help="選択済みのセレクトボックスの内容と閾値を初期化します。"):
            reset_select_box(datalist)

        # セレクトボックスの作成
        create_select_box(datalist)
    else:
        create_multiselect_for_search(datalist)

    return



# セレクトボックス作成関数
def create_select_box(datalist):
    
    # ラベルの初期化
    lis_s_ops_labels = [['Z-子', 'A-親①', 'C-祖父母候補', '', 'B-親②', '', ''],
                        ['子', '親①', '祖父①', '祖母①', '親②', '祖父②', '祖母②']]

    # メッセージ
    lis_label1   = ['メイン血統(検索用)', 'メイン血統(絞込み用)']
    lis_label2   = ['サブ血統(検索用)', 'サブ血統(絞込み用)']
    lis_message1 = ["モンスターのメイン血統を設定します。設定した血統を元に検索を実行します。", 
                   "モンスターのメイン血統を設定します。(絞込み用のため、不要なら設定不要。)"]
    lis_message2 = ["モンスターのサブ血統を設定します。設定した血統を元に検索を実行します。", 
                    "モンスターのサブ血統を設定します。(絞込み用のため、不要なら設定不要。)"]

    # モンスター名設定ラベルの選択
    if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn2:
        ops_choice = 0
    else:
        ops_choice = 1
    
    # セレクトボックス作成
    for i in range(DataList.num_monster):
        col1, col2, col3 = st.columns(DataList.num_kind)

        # 非表示設定を実施。（元々は入力無効として利用していたが、そのままここで流用。元の使い方の部分は据え置き。）
        if not st.session_state.select_ops_disabled[i]:

            # 絞込み用ラベルの選択
            if i == 0 and int(st.session_state.radio_ptn[0]) == DataList.choice_ptn2:
                choice = 0
            else:
                choice = 1
            
            # 見栄え調整のため、ここで頑張る。（入力値を後で補正することもできるが、インパクトが大きいため、ここですべて調整。実際には、きちんと整形した方が見通しは良い。なお、ログは据え置きで、子～祖父②を出力するものとしている。）
            if ops_choice == 0 and i == 2:
                # 変則作成1(2の入力欄を4に入れ替え)
                with col1:
                    st.session_state.session_datalist.lis_names[0][4] = st.selectbox(lis_s_ops_labels[ops_choice][4], st.session_state.select_options[0][4], index = 0, key=f'select_ops_name4', on_change=entry_set_th_from_cmb, args=(datalist, ), disabled=st.session_state.select_ops_disabled[4], help="相性を検索したいモンスター名を設定します。空欄の場合、全モンスターを候補とします。")
                with col2:
                    st.session_state.session_datalist.lis_names[1][4] = st.selectbox(lis_label1[choice],              st.session_state.select_options[1][4], index = 0, key=f'select_ops_main4', on_change=select_set_ops, args=(datalist, 4), disabled=st.session_state.select_ops_disabled[4], help=lis_message1[choice])
                with col3:
                    st.session_state.session_datalist.lis_names[2][4] = st.selectbox(lis_label2[choice],              st.session_state.select_options[2][4], index = 0, key=f'select_ops_sub4', on_change=select_set_ops, args=(datalist, 4), disabled=st.session_state.select_ops_disabled[4], help=lis_message2[choice])
            elif ops_choice == 0 and i == 4:
                # 変則作成2(4の入力欄を2に入れ替え)
                with col1:
                    st.session_state.session_datalist.lis_names[0][2] = st.selectbox(lis_s_ops_labels[ops_choice][2], st.session_state.select_options[0][2], index = 0, key=f'select_ops_name2', on_change=entry_set_th_from_cmb, args=(datalist, ), disabled=st.session_state.select_ops_disabled[2], help="相性を検索したいモンスター名を設定します。空欄の場合、全モンスターを候補とします。")
                with col2:
                    st.session_state.session_datalist.lis_names[1][2] = st.selectbox(lis_label1[choice],              st.session_state.select_options[1][2], index = 0, key=f'select_ops_main2', on_change=select_set_ops, args=(datalist, 2), disabled=st.session_state.select_ops_disabled[2], help=lis_message1[choice])
                with col3:
                    st.session_state.session_datalist.lis_names[2][2] = st.selectbox(lis_label2[choice],              st.session_state.select_options[2][2], index = 0, key=f'select_ops_sub2', on_change=select_set_ops, args=(datalist, 2), disabled=st.session_state.select_ops_disabled[2], help=lis_message2[choice])
            else:
                # 通常作成
                with col1:
                    st.session_state.session_datalist.lis_names[0][i] = st.selectbox(lis_s_ops_labels[ops_choice][i], st.session_state.select_options[0][i], index = 0, key=f'select_ops_name{i}', on_change=entry_set_th_from_cmb, args=(datalist, ), disabled=st.session_state.select_ops_disabled[i], help="相性を検索したいモンスター名を設定します。空欄の場合、全モンスターを候補とします。")
                with col2:
                    st.session_state.session_datalist.lis_names[1][i] = st.selectbox(lis_label1[choice],              st.session_state.select_options[1][i], index = 0, key=f'select_ops_main{i}', on_change=select_set_ops, args=(datalist, i), disabled=st.session_state.select_ops_disabled[i], help=lis_message1[choice])
                with col3:
                    st.session_state.session_datalist.lis_names[2][i] = st.selectbox(lis_label2[choice],              st.session_state.select_options[2][i], index = 0, key=f'select_ops_sub{i}', on_change=select_set_ops, args=(datalist, i), disabled=st.session_state.select_ops_disabled[i], help=lis_message2[choice])

    return



# 子の指定関数
def create_multiselect_for_search(datalist):
        
    # マルチセレクトボックス作成
    selected_items = st.multiselect('育成したい種族を全て入力してください。', datalist.lis_mons_names_only_org, key="search_mons_list")



# 詳細設定欄の作成
def create_details(datalist):

    # 表示
    st.write('')
    st.header('◾詳細設定')
    with st.expander("詳細に設定したい場合はタップまたはクリックしてください。\nなお、モンスター名を設定する前に設定することをお勧めします。"):
        
        # 検索モードラジオボタン作成
        create_radio_button_for_search_mode()

        # 自動検索モードチェックボックス作成
        create_check_box_for_auto_search()

        # 共通秘伝入力エリア作成
        create_number_input_for_common_aff()
        
        # モンスター参照テーブル指定ラジオボタン作成
        create_radio_button(datalist)

        # マルチセレクトボックス作成関数
        create_multiselect(datalist)

        # 計算式選択ボタンの作成
        create_radio_button_exp(datalist)

        # 検索パターン指定ラジオボタン作成
        create_radio_button_ptn(datalist)

        # 検索パターンの絞込みチェックボックス
        create_check_box()

        # 入力エリアの作成
        create_number_input()

        # 閾値自動調整無効化
        create_thresh_disable_check_box(datalist)

    return



# 検索モードラジオボタン作成
def create_radio_button_for_search_mode():

    # 表示
    st.write('')
    st.subheader('▪検索モード', help="検索モードを変更します。通常検索モードはこれまでの検索方式、汎用検索モードは複数種族の子を任意で設定した際に、各子に対して良い結果となる組合せを返す検索方式です。")
        
    # ラジオボタン作成
    c  = st.radio("検索モード",      st.session_state.radio_search_mode_list, horizontal=True, key="radio_search_mode")
    # 他からは「int(st.session_state.radio_search_mode[0])」で参照する。

    return



# 自動検索モードチェックボックス作成
def create_check_box_for_auto_search():

    if int(st.session_state.radio_search_mode[0]) != 2:
        # 表示
        st.write('')
        st.subheader('▪自動検索モード', help="ONにすると、各パラメタを変更する度に検索を実行するようになります。連続して検索したい場合にONにしてください。なお、何か操作するたびに検索するようになるため、処理が重くなります。不要な際にOFFにすることをお勧めします。")
        
        st.checkbox("自動検索モード（試験的なモードです。利用前に必ずマニュアルをご確認ください。）", value=False, key=f"auto_search_mode")

    return



# 共通秘伝入力エリア
def create_number_input_for_common_aff():

    # 表示
    st.write('')
    st.subheader('▪共通秘伝設定', help="各親の共通秘伝について設定できます。")

    # テキスト入力エリアを設定
    col1, col2= st.columns(2)
    with col1:
        st.number_input("共通秘伝Ⅱ", min_value=0, key=f"input_common_aff2")
    with col2:
        st.number_input("共通秘伝Ⅲ", min_value=0, key=f"input_common_aff3")   

    return



# ラジオボタン作成関数
def create_radio_button(datalist):

    if int(st.session_state.radio_search_mode[0]) != 2:
        # 表示
        st.write('')
        st.subheader('▪モンスター参照テーブル', help="子/親祖父母毎に検索で使用するテーブルを設定します。変更時、関連するモンスター名設定をクリアし、閾値を再設定します。")
        
        # テーブル選択結果格納場所の初期化
        st.session_state.session_datalist.lis_choice_table = [int(st.session_state.radio_c[0]), int(st.session_state.radio_pg[0])]
        
        # ラジオボタン作成
        c  = st.radio("子",      st.session_state.radio_table_list[0:3], horizontal=True, key="radio_c", on_change=reset_select_box, args=(datalist, False, True, False, ), help="検索時に使用する子のモンスター名テーブルを設定します。設定内容に合わせて閾値を自動調整します。")
        pg = st.radio("親祖父母", st.session_state.radio_table_list, horizontal=True, key="radio_pg", on_change=reset_select_box, args=(datalist, False, False, True, ), help="検索時に使用する親祖父母のモンスター名テーブルを設定します。設定内容に合わせて閾値を自動調整します。")

        # 値設定
        st.session_state.session_datalist.lis_choice_table[0] = int(c[0])
        st.session_state.session_datalist.lis_choice_table[1] = int(pg[0])
    else:
        # 値設定
        st.session_state.radio_c  = st.session_state.radio_table_list[1]
        st.session_state.radio_pg = st.session_state.radio_table_list[4]
        st.session_state.session_datalist.lis_choice_table[0] = 2
        st.session_state.session_datalist.lis_choice_table[1] = 5

    return



# マルチセレクトボックス作成関数
def create_multiselect(datalist):

    # 表示
    st.write('')
    st.subheader('▪検索除外モンスター指定', help="検索結果に含めたくないモンスターについて選択します。なお、現状では検索開始時に都度候補を外す仕様としています。(処理時間かかるのでよくない)")

    if int(st.session_state.radio_search_mode[0]) != 2:
        lis_mons_names_del = datalist.lis_mons_names_del
    else:
        lis_mons_names_del = datalist.lis_mons_names_del2 
    
    # マルチセレクトボックス作成
    selected_items = st.multiselect('検索結果に含めたくないモンスターがあれば指定してください。', lis_mons_names_del, key="del_mons_list")

    return



# 計算式指定ラジオボタン作成
def create_radio_button_exp(datalist):

    if int(st.session_state.radio_search_mode[0]) != 2:
        # 表示
        st.write('')
        st.subheader('▪計算式', help="相性値を計算する際の計算式を指定します。")

        # ラジオボタン作成
        choice  = st.radio("計算手法",      st.session_state.radio_calc_list, horizontal=True, key="radio_calc", index=1, on_change=entry_set_th_from_cmb, args=(datalist, ), help="相性値を計算する際の計算式を指定します。(m+s)式が現状主流の方式です。")
    else:
        st.session_state.radio_calc = st.session_state.radio_calc_list[1]

    return



# 検索パターン指定ラジオボタン
def create_radio_button_ptn(datalist):

    if int(st.session_state.radio_search_mode[0]) != 2:
        # 表示
        st.write('')
        st.subheader('▪出力パターン', help="全パターンを選択すると、すべての組合せから検索します。特定パターンを選択すると、次のチェックボックスで選択されたパターンのみに絞って検索します。")

        # ラジオボタン作成
        choice  = st.radio("パターン方式",      st.session_state.radio_ptn_list, horizontal=True, key="radio_ptn", index=1, on_change=radio_disable_entry_cmb, args=(datalist, ), help="計算結果の出力パターンを指定します。出力パターンの詳細については補足ページをご確認ください。")
    else:
        st.session_state.radio_ptn = st.session_state.radio_ptn_list[0]
    
    return



# 検索パターン出力形式選択チェックボックス作成
def create_check_box():
    
    if int(st.session_state.radio_search_mode[0]) != 2:
        # ラベル
        lis_s_ops_labels = ['1.Z-ABB×BAA', '2.Z-ABC×BCA', '3.Z-ACC×BCC', 
                            '4.Z-ABB×BCA, Z-ABC×BAA',
                            '5.Z-ABB×BCC, Z-ACC×BAA', 
                            '6.Z-ABC×BCC, Z-ACC×BCA']

        # ヘルプメッセージ
        lis_help_messages =[
            "親と祖父母が入れ替わる形の形式を出力します。",
            "1.の組合せの各親の祖父母どちらか一方を別モンスターに置き換えた形式を出力します。",
            "親①、親②で同じ祖父母を使用するパターンを出力します。",
            "1.と2.の折衷案を出力します。",
            "1.と3.の折衷案を出力します。",
            "2.と3.の折衷案を出力します。",
        ]

        # チェックボックス作成
        st.write("パターン選択")
        for i in range(2):
            col1, col2, col3 = st.columns(3)
            offset = i*3
            with col1:
                st.checkbox(lis_s_ops_labels[offset  ], value=True, key=f"check_ptn{offset  }", disabled=st.session_state.check_ptn_disabled, help=lis_help_messages[offset  ])
            with col2:
                st.checkbox(lis_s_ops_labels[offset+1], value=True, key=f"check_ptn{offset+1}", disabled=st.session_state.check_ptn_disabled, help=lis_help_messages[offset+1])
            with col3:
                st.checkbox(lis_s_ops_labels[offset+2], value=True, key=f"check_ptn{offset+2}", disabled=st.session_state.check_ptn_disabled, help=lis_help_messages[offset+2])

    return



# 閾値入力エリア作成
def create_number_input():

    if int(st.session_state.radio_search_mode[0]) != 2:
        # 表示
        st.write('')
        st.subheader('▪相性値閾値設定', help="本項目での設定値未満の相性値の場合、検索候補から除外します。（よくわからない場合はそのままで問題なし。）")

        # 出力パターンが全パターンの時に表示処理
        if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn1:  

            # ラベルを作成
            label_names = ["a.子-親-祖父-祖母メイン血統の相性値閾値", "b.子-親-祖父-祖母サブ血統の相性値閾値", 
                            "c.親①-親②メイン血統の相性値閾値", "d.親①-親②サブ血統の相性値閾値", 
                            "e.子-親①間のメイン/サブ血統相性値合計閾値", "f.子-親②間のメイン/サブ血統相性値合計閾値",
                            "g.親①家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値", 
                            "h.親②家系の子-祖 or 親-祖間のメイン/サブ血統相性値合計閾値"]

            # テキスト入力エリアを設定
            for i in range(len(label_names)):
                if not st.session_state.input_threshs_disabled[i]:
                    st.number_input(label_names[i], min_value=0, value=st.session_state.session_datalist.lis_threshs[i], key=f"input_thresh{i}", disabled=st.session_state.input_threshs_disabled[i])
        
        else:
            st.write(f"「出力パターン」の項目で「パターン方式」に「1.全パターン」を指定した場合のみ設定可能です。")

    return



# 相性閾値自動変更無効化チェックボックス作成
def create_thresh_disable_check_box(datalist):
    
    if int(st.session_state.radio_search_mode[0]) != 2:
        # 出力パターンが全パターンの時のみ表示
        if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn1:  
            # チェックボックス作成
            st.write("相性値閾値自動設定")
            flag = not st.session_state.check_ptn_disabled
            st.checkbox("無効化", value=False, key="input_threshs_chg_disabled", disabled=flag, on_change=entry_set_th_from_cmb, args=(datalist, ), help="★★注意：無効化すると適切に検索できない場合があります。")

    return



# 検索ボタンの作成
def create_search_button(datalist, used_memory):

    # 表示
    st.write('')
    st.header('◾検索', help="「検索開始！」ボタン押下後に設定値および結果が出力されます。なお、結果は最大5,000件までとなります。また、自動検索モード有効時は基本的に使用しませんが、もし自動検索が動作しない場合はこちらのボタンを使用してください。")

    # 検索ボタン作成(ボタン押下で検索開始)
    if st.button('検索開始！') or st.session_state.auto_search_mode:
        if used_memory < DataList.max_memory_size:
            with st.spinner('processiong...'):
                # 検索
                ret = button_calc_affinity(datalist)
        else:
            st.warning("現在、他のユーザが使用中です。しばらく時間を空けて再度お試しください。なお、しばらくたっても状態が変わらない場合は、管理者にお問い合わせください。")
    
    return



# 結果の表示
def disp_result(datalist, used_memory):

    # 1回以上検索実施されている場合のみ結果等を表示
    if st.session_state.is_search_once_more:

        # 結果の表示
        with st.spinner('processiong...'):
            
            # 結果1件以上で表示
            if len(st.session_state.session_datalist.df_affinities.index) > 0:

                # st.dataframe(st.session_state.session_datalist.df_affinities, width=2000, height=500, use_container_width=True)

                st.write('')
                st.subheader(f"▪検索結果一覧", help="結果一覧が表示されます。相性値列の背景色凡例は次の通りです。黄：☆、緑：◎、水色：〇")
                data1 = set_AgGrid1(datalist, st.session_state.session_datalist.df_affinities)
                
                st.write('')
                st.subheader(f"▪逆引き検索結果一覧", help="結果一覧から選択した最新の1件を元に、親祖父母を固定して再検索します。相性値列等の相性値に関係する列の背景色凡例は次の通りです。黄：☆、緑：◎、水色：〇")
                data2 = set_AgGrid2(datalist, data1)                
        
        # 設定値の表示
        print_log()
        
        # 表示
        st.write(f"現在のメモリ使用量: {used_memory:.2f} MB（デバッグ情報です。）")

    else:
        pass

    return



# 最終結果のデータフレームをAgGridを使用して画面上に配置する
def set_AgGrid1(datalist, df_affinities, add_color_flag=False):

    gb = GridOptionsBuilder.from_dataframe(df_affinities)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    
    gb.configure_column("評価", cellStyle=datalist.cellsytle_jscode)
    if add_color_flag:
        gb.configure_column("親①②", cellStyle=datalist.cellsytle_jscode_parent)
        gb.configure_column("親祖父母①", cellStyle=datalist.cellsytle_jscode_either)
        gb.configure_column("親祖父母②", cellStyle=datalist.cellsytle_jscode_either)
        gb.configure_column("相性値", cellStyle=datalist.cellsytle_jscode_both)
        gb.configure_column("素相性値", cellStyle=datalist.cellsytle_jscode_both)
    # gb.configure_pagination()
    gridOptions = gb.build()
    data = AgGrid(df_affinities, 
        gridOptions=gridOptions, 
        enable_enterprise_modules=True, 
        allow_unsafe_jscode=True, 
        update_mode=GridUpdateMode.SELECTION_CHANGED)
    
    return data



# 逆引き検索結果のデータフレームをAgGridを使用して画面上に配置する
def set_AgGrid2(datalist, data):

    # 検索結果から選択された行をDF化
    selected_rows = data["selected_rows"]

    # 処理
    if selected_rows is not None:

        # 一行以上あれば表示処理

        # ラベルの定義
        label = ['種別', '☆の個数', '◎の個数', '〇の個数', '480以上の個数', '600以上の個数', '平均値', '中央値', '最小値', '最大値']

        ### 順親
        # 選択行設定
        last_ind = len(selected_rows.index)
        temp = selected_rows.iloc[last_ind-1:last_ind, :].values.tolist()
        last_selected_rows = pd.DataFrame(temp, columns=selected_rows.columns.to_list() )
        del last_selected_rows["level_0"]
        del last_selected_rows["評価"]

        # 1件目のレコードを使用して、相性値を計算
        with st.spinner('processiong...'):
            select_calc_affinity(datalist, last_selected_rows, False)
        
        # 選択行に関する統計量
        df_affinities_slct = st.session_state.session_datalist.df_affinities_slct
        mark_st1_1  = (df_affinities_slct.iloc[:, 1] == '☆').sum()
        mark_dci1_1 = (df_affinities_slct.iloc[:, 1] == '◎').sum()
        mark_ci1_1  = (df_affinities_slct.iloc[:, 1] == '〇').sum()
        mark_st1_2  = (df_affinities_slct.iloc[:, 4:6] > 260).sum()
        mark_dci1_2 = (df_affinities_slct.iloc[:, 4:6] > 210).sum() - mark_st1_2
        mark_ci1_2  = (df_affinities_slct.iloc[:, 4:6] > 160).sum() - mark_st1_2 - mark_dci1_2
        num1_1      = (df_affinities_slct.iloc[:, 3] >= 480).sum()
        num1_2      = (df_affinities_slct.iloc[:, 3] >= 600).sum()
        mean1       = df_affinities_slct.iloc[:, 3:6].mean(numeric_only=True)
        med1        = df_affinities_slct.iloc[:, 3:6].median(numeric_only=True)
        min1        = df_affinities_slct.iloc[:, 3:6].min(numeric_only=True)
        max1        = df_affinities_slct.iloc[:, 3:6].max(numeric_only=True)
        statistics1 = pd.DataFrame([["相性値",    mark_st1_1, mark_dci1_1, mark_ci1_1, str(num1_1), str(num1_2), mean1.iloc[0], med1.iloc[0], min1.iloc[0], max1.iloc[0]],
                                    ["親祖父母①", mark_st1_2.iloc[0], mark_dci1_2.iloc[0], mark_ci1_2.iloc[0], "-", "-", mean1.iloc[1], med1.iloc[1], min1.iloc[1], max1.iloc[1]],
                                    ["親祖父母②", mark_st1_2.iloc[1], mark_dci1_2.iloc[1], mark_ci1_2.iloc[1], "-", "-", mean1.iloc[2], med1.iloc[2], min1.iloc[2], max1.iloc[2]]], 
                                    columns=label)

        # まとめて出力
        st.markdown("###### ◎選択行")
        st.dataframe(last_selected_rows, width=2000, height=40, use_container_width=True)
        st.markdown("###### ◎選択行の相性値統計量")
        st.dataframe(statistics1, width=2000, height=150, use_container_width=True)
        st.markdown("###### ◎相性がよさそうな種族候補（ご参考レベル。必ずマニュアルの説明を読むこと。）")
        st.write(f".　　　{st.session_state.session_datalist.str_good_monsters}")
        st.markdown("###### ◎逆引き検索結果")
        set_AgGrid1(datalist, df_affinities_slct, True)
        # st.dataframe(df_affinities_slct, width=1000, height=400, use_container_width=True)


        ### 逆親
        # 逆親設定
        temp = last_selected_rows
        temp_name = "キュービ"
        if int(st.session_state.radio_search_mode[0]) != 2:
            if temp.iloc[0, 1] != "-":
                temp_name = temp.iloc[0, 1]
        else:
            if st.session_state.search_mons_list:
                if st.session_state.search_mons_list[0] != "":
                    temp_name = st.session_state.search_mons_list[0]

        selected_rows_r = pd.DataFrame([[0.0, temp_name, temp.iloc[0, 5], temp.iloc[0, 6], temp.iloc[0, 7], 
                                                               temp.iloc[0, 2], temp.iloc[0, 3], temp.iloc[0, 4]]])
        selected_rows_r.columns = temp.columns.to_list()

        # 相性値を計算
        with st.spinner('processiong...'):
            select_calc_affinity(datalist, selected_rows_r, True)
            
        # 選択行(逆親)に関する統計量
        df_affinities_slct_r = st.session_state.session_datalist.df_affinities_slct_r
        selected_rows_r.iloc[0, 0] = df_affinities_slct_r[df_affinities_slct_r.iloc[:, 2] == selected_rows_r.iloc[0, 1]].iloc[0, 3]
        mark_st2_1  = (df_affinities_slct_r.iloc[:, 1] == '☆').sum()
        mark_dci2_1 = (df_affinities_slct_r.iloc[:, 1] == '◎').sum()
        mark_ci2_1  = (df_affinities_slct_r.iloc[:, 1] == '〇').sum()
        num2_1      = (df_affinities_slct_r.iloc[:, 3] >= 480).sum()
        num2_2      = (df_affinities_slct_r.iloc[:, 3] >= 600).sum()
        mean2       = df_affinities_slct_r.iloc[:, 3:4].mean(numeric_only=True)
        med2        = df_affinities_slct_r.iloc[:, 3:4].median(numeric_only=True)
        # pertile2    = df_affinities_slct_r.quantile(0.8)
        min2        = df_affinities_slct_r.iloc[:, 3:4].min(numeric_only=True)
        max2        = df_affinities_slct_r.iloc[:, 3:4].max(numeric_only=True)
        statistics2 = pd.DataFrame([["相性値", mark_st2_1, mark_dci2_1, mark_ci2_1, num2_1, num2_2, mean2.iloc[0], med2.iloc[0], min2.iloc[0], max2.iloc[0]]],
                                columns=label)

        # まとめて出力
        st.markdown("###### ◎選択行（逆親バージョン）")
        st.dataframe(selected_rows_r, width=2000, height=40, use_container_width=True)
        st.markdown("###### ◎選択行の相性値統計量（逆親バージョン）")
        st.dataframe(statistics2, width=2000, height=50, use_container_width=True)
        st.markdown("###### ◎相性がよさそうな種族候補（ご参考レベル。必ずマニュアルの説明を読むこと。）")
        st.write(f".　　　{st.session_state.session_datalist.str_good_monsters_r}")
        st.markdown("###### ◎逆引き検索結果（逆親バージョン）")
        set_AgGrid1(datalist, df_affinities_slct_r, True)
        # st.dataframe(df_affinities_slct_r, width=1000, height=400, use_container_width=True)


        # 図の出力
        with st.expander("★逆引き検索結果のヒストグラムを表示したい場合はタップまたはクリックしてください。"):
            st.markdown("###### ◎逆引き検索結果のヒストグラム）")
            fig, ax = plt.subplots()
            c1,c2 = "red","blue"
            l1,l2 = "選択行","選択行（逆親）"
            ax.set_xlabel('相性値')
            ax.set_ylabel('頻度')
            ax.grid()
            ax.hist(df_affinities_slct.iloc[:, 3],   bins=30, color=c1, label=l1, range=(350, 650), histtype="stepfilled")
            ax.hist(df_affinities_slct_r.iloc[:, 3], bins=30, color=c2, label=l2, range=(350, 650), histtype="step")
            ax.legend(loc=0)
            st.pyplot(fig, use_container_width=False)

        st.write(f"別の結果を検索する場合は、もう一度選択を実施してください。")
    
    else:
    
        # 選択無なら、メッセージのみ表示
        st.write(f"逆引き検索をする場合は、「検索結果一覧」から、任意のレコードにチェックをつけてください。最後にチェックしたレコードの親祖父母の組合せを元に再計算を実施します。")


