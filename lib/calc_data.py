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
import pandas as pd
# import psutil
# from memory_profiler import profile

# 標準ライブラリ
import collections

# 自作ライブラリ等
# from lib.classes import Monster
# from lib.classes import ThreshAff
from lib.classes import DataList
# from lib.classes import SessionDataList
from lib.process_log import write_log



# 相性基準のマークを返却。★ただし、相性閾値のこと全然知らないので、すべて仮値。
def get_mark(affinity):
    
    mark = "×"
    
    if affinity > 610:
        mark = "☆"
    elif affinity > 490:
        mark = "◎"
    elif affinity > 374:
        mark = "〇"
    elif affinity > 257:
        mark = "△"
    else:
        mark = "×"
    
    return mark



# 上位呼び出し用1
def calc_affinity(Monster_info, thresh_aff, lis_search_mons_ids, datalist):

    if int(st.session_state.radio_search_mode[0]) != 2:
        flag = int(st.session_state.radio_calc[0])
        if flag == DataList.choice_exp1:
            if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn1:  
                return calc_affinity_m(Monster_info, thresh_aff, datalist)
            elif int(st.session_state.radio_ptn[0]) == DataList.choice_ptn2:
                return calc_affinity_m_ptn(Monster_info, datalist)
        elif flag == DataList.choice_exp2:
            if int(st.session_state.radio_ptn[0]) == DataList.choice_ptn1:  
                return calc_affinity_m_s(Monster_info, thresh_aff, datalist)
            elif int(st.session_state.radio_ptn[0]) == DataList.choice_ptn2:
                return calc_affinity_m_s_ptn(Monster_info, datalist)
    else:
        return out_candidates(lis_search_mons_ids, datalist)
        


# 上位呼び出し用2
def calc_affinity_select(Monster_info, datalist):

    flag = int(st.session_state.radio_calc[0])
    if flag == DataList.choice_exp1:
        return calc_affinity_m_select(Monster_info, datalist)
    elif flag == DataList.choice_exp2:
        return calc_affinity_m_s_select(Monster_info, datalist)



# list型→DataFrame型に変換して整形実施。
# calc_affinityの中で実施すること。(エラー処理未実施)
def shape_data(lis_affinities):
    
    # データフレーム型への変換/ソート/ラベル付与/インデックスリセット/上限設定
    df_affinities = pd.DataFrame( lis_affinities )
    df_affinities = df_affinities.sort_values([1, 3], ascending=[False, True])
    df_affinities.columns=['評価', '相性値', '子', '親①', '祖父①', '祖母①', '親②', '祖父②', '祖母②']
    df_affinities = df_affinities.reset_index()
    num_rows = len(df_affinities.index)
    last_row = num_rows if num_rows <= DataList.max_result_num else DataList.max_result_num
    df_affinities = df_affinities.loc[0:last_row, :]

    return df_affinities.reset_index()



def shape_data2(lis_affinities):
    
    # データフレーム型への変換/ソート/ラベル付与/インデックスリセット/上限設定
    df_affinities = pd.DataFrame( lis_affinities )
    df_affinities = df_affinities.drop_duplicates()
    df_affinities = df_affinities.sort_values([1, 3], ascending=[False, True])
    df_affinities.columns=['評価', '選択種族での最小相性値', '選択種族(任意)', '親①', '祖父①', '祖母①', '親②', '祖父②', '祖母②']
    df_affinities = df_affinities.reset_index()
    num_rows = len(df_affinities.index)
    last_row = num_rows if num_rows <= DataList.max_result_num else DataList.max_result_num
    df_affinities = df_affinities.loc[0:last_row, :]

    return df_affinities.reset_index()



# list型→DataFrame型に変換して整形実施。
# calc_affinityの中で実施すること。(エラー処理未実施)
def shape_data_select(lis_affinities):
    
    # データフレーム型への変換/ソート/ラベル付与/インデックスリセット/上限設定
    df_affinities = pd.DataFrame( lis_affinities )
    df_affinities = df_affinities.sort_values([2, 1], ascending=[False, True])
    # ([mark, name_c, all_affinity, cpg1, cpg2, pp, affinity, common_aff])
    df_affinities.columns=['評価', '子', '相性値', "親祖父母①", "親祖父母②", "親①②", "素相性値", "共通秘伝"]
    df_affinities = df_affinities.reset_index()
    num_rows = len(df_affinities.index)
    last_row = num_rows if num_rows <= DataList.max_result_num else DataList.max_result_num
    df_affinities = df_affinities.loc[0:last_row, :]

    return df_affinities.reset_index()



# 相性値全通り計算関数(ひどいforループだ…もっと効率いい方法あるだろ！いい加減にしろ！)。min(m)用
def calc_affinity_m(Monster_info, thresh_aff, datalist):

    # 親①、親②毎に、（子の主血統/副血統、親の主血統/副血統番号）をキーとした
    # 相性値、モンスター名(子/親/祖父/祖母)の6次元配列作成。
    # 6, 5, 4, 3次元目は子の主血統/副血統、2次元目は各「相性値、モンスター名(子/親/祖父/祖母)」のリスト、1次元目で要素アクセス。
    # 2つ出し終わったら、子の主血統/副血統番号が一致するところで、
    # 親①、親②の相性チェックを実施(悪ければ次の親へ)して、親①×親②の相性値も足し合わせ、最終結果を算出。
    # （なお、子の名前の一致不一致で決めてもよいが、レアモンの処理をきちんとしていないため、今回は番号で確認とする。）
    # 最終結果の形式は、判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）でリストに格納し、
    # その後、データフレーム型に変換して、相性値で降順ソートして返却する。
    
    # 返却値
    ret = False
    # 最大値
    N1 = DataList.N1
    N2 = DataList.N2
    N3 = DataList.N3
    # 参照高速化のためにローカル設定
    lis_affinities_m_cp     = datalist.lis_affinities_m_cp
    lis_affinities_s_cp     = datalist.lis_affinities_s_cp
    lis_affinities_m_cpg    = datalist.lis_affinities_m_cpg
    lis_affinities_s_cpg    = datalist.lis_affinities_s_cpg
    lis_mons_league_tb_c    = st.session_state.session_datalist.lis_mons_league_tb_c
    lis_mons_league_tb_pg   = st.session_state.session_datalist.lis_mons_league_tb_pg
    # 保管用リストの作成
    ped1_num = len(lis_mons_league_tb_c)
    ped2_num = len(lis_mons_league_tb_c)
    # lis_affinities_cpg1[child1][child2][parent1][parent2]
    lis_affinities_cpg1 = [[[[ [] for l in range(ped2_num)] for k in range(ped1_num)] for j in range(ped2_num)] for i in range(ped1_num)]
    lis_affinities_cpg2 = [[[[ [] for l in range(ped2_num)] for k in range(ped1_num)] for j in range(ped2_num)] for i in range(ped1_num)]
    lis_affinities      = []
    lis_child1          = []
    lis_child2          = [ [] for j in range(ped1_num) ]
    lis_parent1_1       = []
    lis_parent1_2       = [ [] for j in range(ped1_num) ]
    lis_parent2_1       = []
    lis_parent2_2       = [ [] for j in range(ped1_num) ]
    df_affinities       = pd.DataFrame( [] )
    # 共通秘伝値事前計算
    common_aff = st.session_state.input_common_aff2 * DataList.common_aff2 + st.session_state.input_common_aff3 * DataList.common_aff3
    
    # 子-親①-祖父①-祖母①のメイン/サブ血統(あり得ない組み合わせ、基準値以下はスキップ)
    i = 0
    for child1 in Monster_info[0].ped1_num:
        for parent1 in Monster_info[1].ped1_num:
            for granpa1 in Monster_info[2].ped1_num:
                for granma1 in Monster_info[3].ped1_num:
                    # ここまでで主血統ループ
                    cpg1 = lis_affinities_m_cpg[child1][parent1][granpa1][granma1]
                    if cpg1 < thresh_aff.th_ped1_cpg:
                        continue
                    for child2 in Monster_info[0].ped2_num:
                        name_c = lis_mons_league_tb_c[child1][child2]
                        if name_c == "-":
                            continue
                        for parent2 in Monster_info[1].ped2_num:
                            name_p = lis_mons_league_tb_pg[parent1][parent2]
                            if name_p == "-":
                                continue
                            for granpa2 in Monster_info[2].ped2_num:
                                name_g1 = lis_mons_league_tb_pg[granpa1][granpa2]
                                if name_g1 == "-":
                                    continue
                                for granma2 in Monster_info[3].ped2_num:
                                    name_g2 = lis_mons_league_tb_pg[granma1][granma2]
                                    if name_g2 == "-":
                                        continue
                                    # ここまでで副血統ループ
                                    cpg2 = lis_affinities_s_cpg[child2][parent2][granpa2][granma2]
                                    if cpg2 < thresh_aff.th_ped2_cpg:
                                        continue
                                    lis_affinities_cpg1[child1][child2][parent1][parent2].append([cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    # lis_affinities_cpg1.append([child1, child2, parent1, parent2, cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    if child1 not in lis_child1:
                                        lis_child1.append(child1)
                                    if child2 not in lis_child2[child1]:
                                        lis_child2[child1].append(child2)
                                    if parent1 not in lis_parent1_1:
                                        lis_parent1_1.append(parent1)
                                    if parent2 not in lis_parent1_2[parent1]:
                                        lis_parent1_2[parent1].append(parent2)
                                    i += 1

                                    # 件数チェック
                                    if i >= N1:
                                        st.error(f"子-親①-祖父①-祖母①の組み合わせ候補が{N1}件を超えたため停止します。\n子 親 祖父 祖母メイン血統に関する閾値やモンスター参照テーブルの見直しを実施してください。")
                                        return ret, df_affinities

    write_log(f"◎子-親①-祖父①-祖母①の組み合わせ：{i:,}件")
    if i == 0:
        st.error(f"子-親①-祖父①-祖母①の組み合わせ候補が0件のため停止します。\n子 親 祖父 祖母メイン血統に関する閾値やモンスター参照テーブルの見直しを実施してください。")
        return ret, df_affinities
    
    # 子-親②-祖父②-祖母②のメイン/サブ血統(あり得ない組み合わせ、基準値以下はスキップ)
    j = 0
    for child1 in lis_child1:
        for parent1 in Monster_info[4].ped1_num:
            for granpa1 in Monster_info[5].ped1_num:
                for granma1 in Monster_info[6].ped1_num:
                    # ここまでで主血統ループ
                    cpg1 = lis_affinities_m_cpg[child1][parent1][granpa1][granma1]
                    if cpg1 < thresh_aff.th_ped1_cpg:
                        continue
                    for child2 in lis_child2[child1]:
                        name_c = lis_mons_league_tb_c[child1][child2]
                        if name_c == "-":
                            continue
                        for parent2 in Monster_info[4].ped2_num:
                            name_p = lis_mons_league_tb_pg[parent1][parent2]
                            if name_p == "-":
                                continue
                            for granpa2 in Monster_info[5].ped2_num:
                                name_g1 = lis_mons_league_tb_pg[granpa1][granpa2]
                                if name_g1 == "-":
                                    continue
                                for granma2 in Monster_info[6].ped2_num:
                                    name_g2 = lis_mons_league_tb_pg[granma1][granma2]
                                    if name_g2 == "-":
                                        continue
                                    # ここまでで副血統ループ
                                    cpg2 = lis_affinities_s_cpg[child2][parent2][granpa2][granma2]
                                    if cpg2 < thresh_aff.th_ped2_cpg:
                                        continue
                                    # name_cの格納は不要だが、同形状のリストの方がバグを回避できそうなためそのままとする。
                                    # lis_affinities_cpg2.append([child1, child2, parent1, parent2, cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    lis_affinities_cpg2[child1][child2][parent1][parent2].append([cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    if parent1 not in lis_parent2_1:
                                        lis_parent2_1.append(parent1)
                                    if parent2 not in lis_parent2_2[parent1]:
                                        lis_parent2_2[parent1].append(parent2)
                                    j += 1
                                    if j >= N2:
                                        st.error(f"子-親②-祖父②-祖母②の組み合わせ候補が{N2}件を超えたため停止します。\n子 親 祖父 祖母サブ血統に関する閾値やモンスター参照テーブルの見直しを実施してください。")
                                        return ret, df_affinities
    
    
    write_log(f"◎子-親②-祖父②-祖母②の組み合わせ：{j:,}件")
    if j == 0:
        st.error(f"子-親②-祖父②-祖母②の組み合わせ候補が0件のため停止します。\n子 親 祖父 祖母メイン血統に関する閾値やモンスター参照テーブルの見直しを実施してください。")
        return ret, df_affinities
    
    # 親①-親②のメイン/サブ血統(基準値以下はスキップ)
    k = 0
    for child1 in lis_child1:
        for child2 in lis_child2[child1]:
            for parent1_1 in lis_parent1_1:
                for parent2_1 in lis_parent2_1:
                    pp1 = lis_affinities_m_cp[ parent1_1 ][ parent2_1 ]
                    if pp1 < thresh_aff.th_ped1_pp:
                        continue
                    for parent1_2 in lis_parent1_2[parent1_1]:
                        for parent2_2 in lis_parent2_2[parent2_1]:
                            pp2 = lis_affinities_s_cp[ parent1_2 ][ parent2_2 ]
                            if pp2 < thresh_aff.th_ped2_pp:
                                continue
                            for cpg1_record in lis_affinities_cpg1[child1][child2][parent1_1][parent1_2]:
                                for cpg2_record in lis_affinities_cpg2[child1][child2][parent2_1][parent2_2]:
                                    affinity = pp1 + pp2 + cpg1_record[0] + cpg2_record[0] + common_aff
                                    mark = get_mark(affinity)
                                    # 判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）
                                    lis_affinities.append([mark, affinity, 
                                                        cpg1_record[1], cpg1_record[2], 
                                                        cpg1_record[3], cpg1_record[4], 
                                                                        cpg2_record[2], 
                                                        cpg2_record[3], cpg2_record[4]] )
                                    k += 1
                                    if k >= N3:
                                        st.error(f"子-両親-祖父母①-祖父母②の組み合わせ候補が{N3}件を超えたため停止します。\n親①-親②間に関する閾値やモンスター参照テーブルの見直しを実施してください。")
                                        return ret, df_affinities


    write_log(f"◎子-両親-祖父母①-祖父母②の組み合わせ：{len(lis_affinities):,}件")
    if len(lis_affinities) == 0:
        st.error(f"子-両親-祖父母①-祖父母②の組み合わせ候補が0件です。\n親①-親②関する閾値やモンスター参照テーブルの見直しを実施してください。")
        return ret, df_affinities

    # データ整形
    df_affinities = shape_data(lis_affinities)

    # 返却値設定
    ret = True

    return ret, df_affinities



# 相性値全通り計算関数(ひどいforループだ…もっと効率いい方法あるだろ！いい加減にしろ！)。min(m+s)用。
def calc_affinity_m_s(Monster_info, thresh_aff, datalist):

    # 愚直に計算。
    # min(m)とやり方は近く、事前計算できなくなった分、本関数で追加で実施している箇所あり。
    
    # 返却値
    ret = False
    # 最大値
    N1 = DataList.N1
    N2 = DataList.N2
    N3 = DataList.N3
    # 参照高速化のためにローカル設定
    lis_affinities_m_s_cp   = datalist.lis_affinities_m_s_cp
    lis_affinities_m_cp     = datalist.lis_affinities_m_cp
    lis_affinities_s_cp     = datalist.lis_affinities_s_cp
    lis_mons_league_tb_c    = st.session_state.session_datalist.lis_mons_league_tb_c
    lis_mons_league_tb_pg   = st.session_state.session_datalist.lis_mons_league_tb_pg
    # 保管用リストの作成
    ped1_num = len(lis_mons_league_tb_c)
    ped2_num = len(lis_mons_league_tb_c)
    # lis_affinities_cpg1[child1][child2][parent1][parent2]
    lis_affinities_cpg1 = [[[[ [] for l in range(ped2_num)] for k in range(ped1_num)] for j in range(ped2_num)] for i in range(ped1_num)]
    lis_affinities_cpg2 = [[[[ [] for l in range(ped2_num)] for k in range(ped1_num)] for j in range(ped2_num)] for i in range(ped1_num)]
    lis_affinities      = []
    lis_child1          = []
    lis_child2          = [ [] for j in range(ped1_num) ]
    lis_parent1_1       = []
    lis_parent1_2       = [ [] for j in range(ped1_num) ]
    lis_parent2_1       = []
    lis_parent2_2       = [ [] for j in range(ped1_num) ]
    df_affinities       = pd.DataFrame( [] )
    # 共通秘伝値事前計算
    common_aff = st.session_state.input_common_aff2 * DataList.common_aff2 + st.session_state.input_common_aff3 * DataList.common_aff3

    # 子-親①-祖父①-祖母①のメイン/サブ血統(あり得ない組み合わせ、基準値以下はスキップ)
    i = 0
    # 子
    for child1 in Monster_info[0].ped1_num:
        for child2 in Monster_info[0].ped2_num:
            name_c = lis_mons_league_tb_c[child1][child2]
            if name_c == "-":
                continue
            
            # 親
            for parent1 in Monster_info[1].ped1_num:
                for parent2 in Monster_info[1].ped2_num:
                    name_p = lis_mons_league_tb_pg[parent1][parent2]
                    if name_p == "-":
                        continue
                    cp = lis_affinities_m_s_cp[child1][child2][parent1][parent2]
                    if cp < thresh_aff.th_p1:
                        continue
                    
                    # 祖父
                    for granpa1 in Monster_info[2].ped1_num:
                        for granpa2 in Monster_info[2].ped2_num:
                            name_g1 = lis_mons_league_tb_pg[granpa1][granpa2]
                            if name_g1 == "-":
                                continue
                            cg1 = lis_affinities_m_s_cp[child1][child2][granpa1][granpa2]
                            pg1 = lis_affinities_m_s_cp[parent1][parent2][granpa1][granpa2]
                            cpg1 = cg1 if cg1 < pg1 else pg1
                            if cpg1 < thresh_aff.th_cpg1:
                                continue

                            # 祖母
                            for granma1 in Monster_info[3].ped1_num:
                                for granma2 in Monster_info[3].ped2_num:
                                    name_g2 = lis_mons_league_tb_pg[granma1][granma2]
                                    if name_g2 == "-":
                                        continue
                                    cg2 = lis_affinities_m_s_cp[child1][child2][granma1][granma2]
                                    pg2 = lis_affinities_m_s_cp[parent1][parent2][granma1][granma2]
                                    cpg2 = cg2 if cg2 < pg2 else pg2
                                    if cpg2 < thresh_aff.th_cpg1:
                                        continue

                                    # 格納
                                    lis_affinities_cpg1[child1][child2][parent1][parent2].append([cp + cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    if child1 not in lis_child1:
                                        lis_child1.append(child1)
                                    if child2 not in lis_child2[child1]:
                                        lis_child2[child1].append(child2)
                                    if parent1 not in lis_parent1_1:
                                        lis_parent1_1.append(parent1)
                                    if parent2 not in lis_parent1_2[parent1]:
                                        lis_parent1_2[parent1].append(parent2)
                                    i += 1

                                    # 件数チェック
                                    if i >= N1:
                                        st.error(f"子-親①-祖父①-祖母①の組み合わせ候補が{N1}件を超えたため停止します。\n子-親①間、親①家系に関する閾値やモンスター参照テーブルの見直しを実施してください。")
                                        return ret, df_affinities
                                    
    write_log(f"◎子-親①-祖父①-祖母①の組み合わせ：{i:,}件")
    if i == 0:
        st.error(f"子-親①-祖父①-祖母①の組み合わせ候補が0件のため停止します。\n子-親①間、親①家系に関する閾値やモンスター参照テーブルの見直しを実施してください。")
        return ret, df_affinities
    
    # 子-親②-祖父②-祖母②のメイン/サブ血統(あり得ない組み合わせ、基準値以下はスキップ)
    j = 0
    # 子
    for child1 in lis_child1:
        for child2 in lis_child2[child1]:
            name_c = lis_mons_league_tb_c[child1][child2]
            if name_c == "-":
                continue
            
            # 親
            for parent1 in Monster_info[4].ped1_num:
                for parent2 in Monster_info[4].ped2_num:
                    name_p = lis_mons_league_tb_pg[parent1][parent2]
                    if name_p == "-":
                        continue
                    cp = lis_affinities_m_s_cp[child1][child2][parent1][parent2]
                    if cp < thresh_aff.th_p2:
                        continue

                    # 祖父
                    for granpa1 in Monster_info[5].ped1_num:
                        for granpa2 in Monster_info[5].ped2_num:
                            name_g1 = lis_mons_league_tb_pg[granpa1][granpa2]
                            if name_g1 == "-":
                                continue
                            cg1 = lis_affinities_m_s_cp[child1][child2][granpa1][granpa2]
                            pg1 = lis_affinities_m_s_cp[parent1][parent2][granpa1][granpa2]
                            cpg1 = cg1 if cg1 < pg1 else pg1
                            if cpg1 < thresh_aff.th_cpg2:
                                continue

                            # 祖母
                            for granma1 in Monster_info[6].ped1_num:
                                for granma2 in Monster_info[6].ped2_num:
                                    name_g2 = lis_mons_league_tb_pg[granma1][granma2]
                                    if name_g2 == "-":
                                        continue
                                    cg2 = lis_affinities_m_s_cp[child1][child2][granma1][granma2]
                                    pg2 = lis_affinities_m_s_cp[parent1][parent2][granma1][granma2]
                                    cpg2 = cg2 if cg2 < pg2 else pg2
                                    if cpg2 < thresh_aff.th_cpg2:
                                        continue

                                    # 格納
                                    # name_cの格納は不要だが、同形状のリストの方がバグを回避できそうなためそのままとする。
                                    lis_affinities_cpg2[child1][child2][parent1][parent2].append([cp + cpg1 + cpg2, name_c, name_p, name_g1, name_g2])
                                    if parent1 not in lis_parent2_1:
                                        lis_parent2_1.append(parent1)
                                    if parent2 not in lis_parent2_2[parent1]:
                                        lis_parent2_2[parent1].append(parent2)
                                    j += 1
                                    if j >= N2:
                                        st.error(f"子-親②-祖父②-祖母②の組み合わせ候補が{N2}件を超えたため停止します。\n子-親②間、親②家系に関する閾値やモンスター参照テーブルの見直しを実施してください。")
                                        return ret, df_affinities
    
    write_log(f"◎子-親②-祖父②-祖母②の組み合わせ：{j:,}件")
    if j == 0:
        st.error(f"子-親②-祖父②-祖母②の組み合わせ候補が0件のため停止します。\n子-親①間、親①家系に関する閾値やモンスター参照テーブルの見直しを実施してください。")
        return ret, df_affinities
    
    # 親①-親②のメイン/サブ血統(基準値以下はスキップ)
    k = 0
    for child1 in lis_child1:
        for child2 in lis_child2[child1]:
            for parent1_1 in lis_parent1_1:
                for parent2_1 in lis_parent2_1:
                    pp1 = lis_affinities_m_cp[ parent1_1 ][ parent2_1 ]
                    if pp1 < thresh_aff.th_ped1_pp:
                        continue
                    for parent1_2 in lis_parent1_2[parent1_1]:
                        for parent2_2 in lis_parent2_2[parent2_1]:
                            pp2 = lis_affinities_s_cp[ parent1_2 ][ parent2_2 ]
                            if pp2 < thresh_aff.th_ped2_pp:
                                continue
                            for cpg1_record in lis_affinities_cpg1[child1][child2][parent1_1][parent1_2]:
                                for cpg2_record in lis_affinities_cpg2[child1][child2][parent2_1][parent2_2]:
                                    affinity = pp1 + pp2 + cpg1_record[0] + cpg2_record[0] + common_aff
                                    mark = get_mark(affinity)
                                    # 判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）
                                    lis_affinities.append([mark, affinity, 
                                                        cpg1_record[1], cpg1_record[2], 
                                                        cpg1_record[3], cpg1_record[4], 
                                                                        cpg2_record[2], 
                                                        cpg2_record[3], cpg2_record[4]] )
                                    k += 1
                                    if k >= N3:
                                        st.error(f"子-両親-祖父母①-祖父母②の組み合わせ候補が{N3}件を超えたため停止します。\n親①-親②間に関する閾値やモンスター参照テーブルの見直しを実施してください。")
                                        return ret, df_affinities

    write_log(f"◎子-両親-祖父母①-祖父母②の組み合わせ：{len(lis_affinities):,}件")
    if len(lis_affinities) == 0:
        st.error(f"子-両親-祖父母①-祖父母②の組み合わせ候補が0件です。\n親①-親②関する閾値やモンスター参照テーブルの見直しを実施してください。")
        return ret, df_affinities

    # データ整形
    df_affinities = shape_data(lis_affinities)

    # 返却値設定
    ret = True

    return ret, df_affinities



# リスト内の重複をチェックするローカル関数を定義
def has_duplicates(seq):
    return len(seq) != len(set(seq))



# モンスターの指定で重複がないかチェックする。(True:重複有、False:重複無)
def check_name(Monster_info):
    
    ret = False
    
    # 一旦リストに格納
    mons_names = []
    if Monster_info[0].name != "":
        mons_names.append(Monster_info[0].name)
    if Monster_info[1].name != "":
        mons_names.append(Monster_info[1].name)
    if Monster_info[2].name != "":
        mons_names.append(Monster_info[2].name)
    if Monster_info[4].name != "":
        mons_names.append(Monster_info[4].name)

    # 重複チェックなど
    if len(mons_names) > 1:
        ret = has_duplicates(mons_names)

    return ret


# 相性値全通り計算関数(ひどいforループだ…もっと効率いい方法あるだろ！いい加減にしろ！)。min(m)用
def calc_affinity_m_ptn(Monster_info, datalist):

    # 親①、親②毎に、（子の主血統/副血統、親の主血統/副血統番号）をキーとした
    # 相性値、モンスター名(子/親/祖父/祖母)の6次元配列作成。
    # 6, 5, 4, 3次元目は子の主血統/副血統、2次元目は各「相性値、モンスター名(子/親/祖父/祖母)」のリスト、1次元目で要素アクセス。
    # 2つ出し終わったら、子の主血統/副血統番号が一致するところで、
    # 親①、親②の相性チェックを実施(悪ければ次の親へ)して、親①×親②の相性値も足し合わせ、最終結果を算出。
    # （なお、子の名前の一致不一致で決めてもよいが、レアモンの処理をきちんとしていないため、今回は番号で確認とする。）
    # 最終結果の形式は、判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）でリストに格納し、
    # その後、データフレーム型に変換して、相性値で降順ソートして返却する。
    
    # 返却値
    ret = False
    # 参照高速化のためにローカル設定
    lis_affinities_m_cpg    = datalist.lis_affinities_m_cpg
    lis_affinities_s_cpg    = datalist.lis_affinities_s_cpg
    lis_affinities_m_s_cp   = datalist.lis_affinities_m_s_cp
    lis_mons_league_tb_c    = st.session_state.session_datalist.lis_mons_league_tb_c
    lis_mons_league_tb_pg   = st.session_state.session_datalist.lis_mons_league_tb_pg
    # lis_affinities_cpg1[child1][child2][parent1][parent2]
    lis_affinities      = []
    df_affinities       = pd.DataFrame( [] )
    # 共通秘伝値事前計算
    common_aff = st.session_state.input_common_aff2 * DataList.common_aff2 + st.session_state.input_common_aff3 * DataList.common_aff3

    # 重複チェック
    if check_name(Monster_info):
        st.error(f"Z-子, A-親①, B-親②, C-祖父母候補のモンスターで同名のモンスターが指定されています。\n異なるモンスターを指定するか削除するかで対応してください。同名モンスターについて検索したい場合は、全パターン方式を使用してください。")
        return ret, df_affinities

    # 閾値(空っぽ)
    if (st.session_state.session_datalist.lis_choice_table[1] == DataList.choice_table_only_org or
        st.session_state.session_datalist.lis_choice_table[1] == DataList.choice_table_only_rare):
        # 親祖父母テーブルが純血統のみ、レアモンのみの場合
        thresh1 = 94
        thresh2 = 94
        thresh3 = 62
    else:
        thresh1 = 102
        thresh2 = 102
        thresh3 = 70

    # 閾値(血統指定)
    if Monster_info[0].pedigree1 != "" and Monster_info[0].pedigree2 != "":
        thresh1 = 87
        thresh2 = 87
        thresh3 = 62
    elif Monster_info[0].pedigree1 != "" or Monster_info[0].pedigree2 != "":
        thresh1 = 93
        thresh2 = 93
        thresh3 = 65

    # 閾値(子親祖父普通用)
    i = 0
    for monster in Monster_info:
        if monster.name != "":
            thresh1 = 87
            thresh2 = 87
            thresh3 = 62
            i += 1

    # 閾値(祖父レアモン用)
    if len(Monster_info[2].ped2_num) == 1 and Monster_info[2].ped2_num[0] == 0:
        thresh1 = 87
        thresh2 = 87
        thresh3 = 60

    # 閾値(親レアモン用)
    if (len(Monster_info[1].ped2_num) == 1 and Monster_info[1].ped2_num[0] == 0) or (len(Monster_info[4].ped2_num) == 1 and Monster_info[4].ped2_num[0] == 0):
        thresh1 = 80
        thresh2 = 80
        thresh3 = 57

    # 閾値(子レアモン用)
    if len(Monster_info[0].ped2_num) == 1 and Monster_info[0].ped2_num[0] == 0:
        thresh1 = 70
        thresh2 = 70
        thresh3 = 53
    
    # 2つ以上指定されている場合は、閾値を無効化。
    if i >=2:
        thresh1 = 1
        thresh2 = 1
        thresh3 = 1

    # フラグ
    c_is_not_1 = False if len(Monster_info[2].ped1_num) == 1 or len(Monster_info[2].ped2_num) == 1 else True
    
    # 指定された4体のモンスター同士の相性を計算
    for z_m in Monster_info[0].ped1_num:
        for a_m in Monster_info[1].ped1_num:
            for b_m in Monster_info[4].ped1_num:
                zabb_m = lis_affinities_m_cpg[z_m][a_m][b_m][b_m]
                if zabb_m < thresh1:
                    continue
                zbaa_m = lis_affinities_m_cpg[z_m][b_m][a_m][a_m]
                if zbaa_m < thresh1:
                    continue

                for z_s in Monster_info[0].ped2_num:
                    name_z = lis_mons_league_tb_c[z_m][z_s]
                    if name_z == "-":
                        continue
                    for a_s in Monster_info[1].ped2_num:
                        name_a = lis_mons_league_tb_pg[a_m][a_s]
                        if name_a == "-":
                            continue
                        if name_z == name_a:
                            continue
                        for b_s in Monster_info[4].ped2_num:
                            name_b = lis_mons_league_tb_pg[b_m][b_s]
                            if name_b == "-":
                                continue
                            if name_z == name_b or name_a == name_b:
                                continue
                            zabb_s = lis_affinities_s_cpg[z_s][a_s][b_s][b_s]
                            if zabb_s < thresh2:
                                continue
                            zbaa_s = lis_affinities_s_cpg[z_s][b_s][a_s][a_s]
                            if zbaa_s < thresh2:
                                continue
                            ab = lis_affinities_m_s_cp[a_m][a_s][b_m][b_s]
                            if ab < thresh3:
                                continue
                            ab_common = ab + common_aff
                            
                            # 事前に一部計算
                            z_abb = zabb_m + zabb_s
                            z_baa = zbaa_m + zbaa_s 

                            # 各パターンについて計算して
                            # 判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）でリストに結果を格納。
                            # Z-ABB×BAA
                            if st.session_state.check_ptn0:
                                if c_is_not_1:
                                    aff0 = ab_common + z_abb + z_baa 
                                    mark0 = get_mark(aff0)
                                    lis_affinities.append([mark0, aff0, name_z, name_a, name_b, name_b, name_b, name_a, name_a] )

                            for c_m in Monster_info[2].ped1_num:
                                zacc_m = lis_affinities_m_cpg[z_m][a_m][c_m][c_m]
                                if zacc_m < thresh1:
                                    continue
                                zbcc_m = lis_affinities_m_cpg[z_m][b_m][c_m][c_m]
                                if zbcc_m < thresh1:
                                    continue
                                zabc_m = lis_affinities_m_cpg[z_m][a_m][b_m][c_m]
                                if zabc_m < thresh1:
                                    continue
                                zbca_m = lis_affinities_m_cpg[z_m][b_m][c_m][a_m]
                                if zbca_m < thresh1:
                                    continue
                                
                                for c_s in Monster_info[2].ped2_num:
                                    name_c = lis_mons_league_tb_pg[c_m][c_s]
                                    if name_c == "-":
                                        continue
                                    if name_z == name_c or name_a == name_c or  name_b == name_c:
                                        continue
                                    zacc_s = lis_affinities_s_cpg[z_s][a_s][c_s][c_s]
                                    if zacc_s < thresh2:
                                        continue
                                    zbcc_s = lis_affinities_s_cpg[z_s][b_s][c_s][c_s]
                                    if zbcc_s < thresh2:
                                        continue
                                    zabc_s = lis_affinities_s_cpg[z_s][a_s][b_s][c_s]
                                    if zabc_s < thresh2:
                                        continue
                                    zbca_s = lis_affinities_s_cpg[z_s][b_s][c_s][a_s]
                                    if zbca_s < thresh2:
                                        continue

                                    # 事前に一部計算
                                    z_abc = zabc_m + zabc_s
                                    z_bca = zbca_m + zbca_s
                                    z_acc = zacc_m + zacc_s
                                    z_bcc = zbcc_m + zbcc_s 

                                    # 各パターンについて計算して
                                    # 判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）でリストに結果を格納。
                                    # Z-ABC×BCA
                                    if st.session_state.check_ptn1:
                                        aff1 = ab_common + z_abc + z_bca 
                                        mark1 = get_mark(aff1)
                                        lis_affinities.append([mark1, aff1, name_z, name_a, name_b, name_c, name_b, name_c, name_a] )
                                    
                                    # Z-ACC×BCC
                                    if st.session_state.check_ptn2:
                                        aff2 = ab_common + z_acc + z_bcc 
                                        mark2 = get_mark(aff2)
                                        lis_affinities.append([mark2, aff2, name_z, name_a, name_c, name_c, name_b, name_c, name_c] )

                                    # Z-ABB×BCA, Z-ABC×BAA
                                    if st.session_state.check_ptn3:
                                        aff3_1 = ab_common + z_abb + z_bca 
                                        aff3_2 = ab_common + z_abc + z_baa 
                                        mark3_1 = get_mark(aff3_1)
                                        lis_affinities.append([mark3_1, aff3_1, name_z, name_a, name_b, name_b, name_b, name_c, name_a] )
                                        mark3_2 = get_mark(aff3_2)
                                        lis_affinities.append([mark3_2, aff3_2, name_z, name_a, name_b, name_c, name_b, name_a, name_a] ) 
                                    
                                    # Z-ABB×BCC, Z-ACC×BAA
                                    if st.session_state.check_ptn4:
                                        aff4_1 = ab_common + z_abb + z_bcc
                                        aff4_2 = ab_common + z_acc + z_baa
                                        mark4_1 = get_mark(aff4_1)
                                        lis_affinities.append([mark4_1, aff4_1, name_z, name_a, name_b, name_b, name_b, name_c, name_c] ) 
                                        mark4_2 = get_mark(aff4_2)
                                        lis_affinities.append([mark4_2, aff4_2, name_z, name_a, name_c, name_c, name_b, name_a, name_a] ) 

                                    # Z-ABC×BCC, Z-ACC×BCA
                                    if st.session_state.check_ptn5:
                                        aff5_1 = ab_common + z_abc + z_bcc
                                        aff5_2 = ab_common + z_acc + z_bca
                                        mark5_1 = get_mark(aff5_1)
                                        lis_affinities.append([mark5_1, aff5_1, name_z, name_a, name_b, name_c, name_b, name_c, name_c] ) 
                                        mark5_2 = get_mark(aff5_2)
                                        lis_affinities.append([mark5_2, aff5_2, name_z, name_a, name_c, name_c, name_b, name_c, name_a] ) 

    write_log(f"◎子-両親-祖父母①-祖父母②の組み合わせ：{len(lis_affinities):,}件")
    if len(lis_affinities) == 0:
        st.error(f"子-両親-祖父母①-祖父母②の組み合わせ候補が0件です。\n他の検索手法を利用してください。")
        return ret, df_affinities

    # データ整形
    df_affinities = shape_data(lis_affinities)

    # 返却値設定
    ret = True

    return ret, df_affinities



# 相性値全通り計算関数(ひどいforループだ…もっと効率いい方法あるだろ！いい加減にしろ！)。min(m+s)用。
# Monsterinfoには、子、親①、親②、祖父の4つの情報のみ格納。
def calc_affinity_m_s_ptn(Monster_info, datalist):

    # 愚直に計算。
    # min(m)とやり方は近く、事前計算できなくなった分、本関数で追加で実施している箇所あり。
    
    # 返却値
    ret = False
    # 参照高速化のためにローカル設定
    lis_affinities_m_s_cp   = datalist.lis_affinities_m_s_cp
    lis_mons_league_tb_c    = st.session_state.session_datalist.lis_mons_league_tb_c
    lis_mons_league_tb_pg   = st.session_state.session_datalist.lis_mons_league_tb_pg
    # 保管用リストの作成
    lis_affinities      = []
    df_affinities       = pd.DataFrame( [] )
    # 共通秘伝値事前計算
    common_aff = st.session_state.input_common_aff2 * DataList.common_aff2 + st.session_state.input_common_aff3 * DataList.common_aff3

    # 重複チェック
    if check_name(Monster_info):
        st.error(f"Z-子, A-親①, B-親②, C-祖父母候補のモンスターで同名のモンスターが指定されています。\n異なるモンスターを指定するか削除するかで対応してください。同名モンスターについて検索したい場合は、全パターン方式を使用してください。")
        return ret, df_affinities

    # 閾値(空っぽ)
    if (st.session_state.session_datalist.lis_choice_table[1] == DataList.choice_table_only_org or
        st.session_state.session_datalist.lis_choice_table[1] == DataList.choice_table_only_rare):
        # 親祖父母テーブルが純血統のみ、レアモンのみの場合
        thresh1 = 62
        thresh2 = 62
        thresh3 = 62
    else:
        thresh1 = 70
        thresh2 = 70
        thresh3 = 70

    # 閾値(血統指定)
    if Monster_info[0].pedigree1 != "" and Monster_info[0].pedigree2 != "":
        thresh1 = 62
        thresh2 = 62
        thresh3 = 62
    elif Monster_info[0].pedigree1 != "" or Monster_info[0].pedigree2 != "":
        thresh1 = 65
        thresh2 = 65
        thresh3 = 65

    # 閾値(子親祖父普通用)
    i = 0
    for monster in Monster_info:
        if monster.name != "":
            thresh1 = 62
            thresh2 = 62
            thresh3 = 62
            i += 1

    # 閾値(祖父レアモン用)
    if len(Monster_info[2].ped2_num) == 1 and Monster_info[2].ped2_num[0] == 0:
        thresh1 = 62
        thresh2 = 62
        thresh3 = 60

    # 閾値(親レアモン用)
    if (len(Monster_info[1].ped2_num) == 1 and Monster_info[1].ped2_num[0] == 0) or (len(Monster_info[4].ped2_num) == 1 and Monster_info[4].ped2_num[0] == 0):
        thresh1 = 57
        thresh2 = 57
        thresh3 = 57

    # 閾値(子レアモン用)
    if len(Monster_info[0].ped2_num) == 1 and Monster_info[0].ped2_num[0] == 0:
        thresh1 = 53
        thresh2 = 53
        thresh3 = 53

    # 2つ以上指定されている場合は、閾値を無効化。
    if i >=2:
        thresh1 = 1
        thresh2 = 1
        thresh3 = 1

    # フラグ
    c_is_not_1 = False if len(Monster_info[2].ped1_num) == 1 or len(Monster_info[2].ped2_num) == 1 else True

    # 指定された4体のモンスター同士の相性を計算
    # 子
    for z_m in Monster_info[0].ped1_num:
        for z_s in Monster_info[0].ped2_num:
            name_z = lis_mons_league_tb_c[z_m][z_s]
            if name_z == "-":
               continue
            
            # 親①
            for a_m in Monster_info[1].ped1_num:
                for a_s in Monster_info[1].ped2_num:
                    name_a = lis_mons_league_tb_pg[a_m][a_s]
                    if name_a == "-":
                        continue
                    if name_z == name_a:
                        continue
                    za = lis_affinities_m_s_cp[z_m][z_s][a_m][a_s]
                    if za < thresh1:
                        continue

                    # 親②
                    for b_m in Monster_info[4].ped1_num:
                        for b_s in Monster_info[4].ped2_num:
                            name_b = lis_mons_league_tb_pg[b_m][b_s]
                            if name_b == "-":
                                continue
                            if name_z == name_b or name_a == name_b:
                                continue
                            zb = lis_affinities_m_s_cp[z_m][z_s][b_m][b_s]
                            if zb < thresh1:
                                continue
                            ab = lis_affinities_m_s_cp[a_m][a_s][b_m][b_s]
                            if ab < thresh2:
                                continue
                            ba = lis_affinities_m_s_cp[b_m][b_s][a_m][a_s]
                            if ba < thresh2:
                                continue

                            # 子→親①、子→親②、親①→親②、共通秘伝の事前計算
                            aff_base = za + zb + ab + common_aff

                            # 子→祖父、親→祖父に関する事前計算
                            zbab = min(zb, ab)
                            zaba = min(za, ba)

                            # 事前に一部計算
                            z_abb = zbab*2
                            z_baa = zaba*2

                            # 各パターンについて計算して
                            # 判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）でリストに結果を格納。

                            # Z-ABB×BAA
                            if st.session_state.check_ptn0:
                                if c_is_not_1:
                                    aff1 = aff_base + z_abb + z_baa
                                    mark1 = get_mark(aff1)
                                    lis_affinities.append([mark1, aff1, name_z, name_a, name_b, name_b, name_b, name_a, name_a] )

                            # 祖父等
                            for c_m in Monster_info[2].ped1_num:
                                for c_s in Monster_info[2].ped2_num:
                                    name_c = lis_mons_league_tb_pg[c_m][c_s]
                                    if name_c == "-":
                                        continue
                                    if name_z == name_c or name_a == name_c or  name_b == name_c:
                                        continue
                                    zc = lis_affinities_m_s_cp[z_m][z_s][c_m][c_s]
                                    if zc < thresh1:
                                        continue
                                    ac = lis_affinities_m_s_cp[a_m][a_s][c_m][c_s]
                                    if ac < thresh3:
                                        continue
                                    bc = lis_affinities_m_s_cp[b_m][b_s][c_m][c_s]
                                    if bc < thresh3:
                                        continue                                    

                                    # 子→祖父、親→祖父に関する事前計算
                                    zcac = min(zc, ac)
                                    zcbc = min(zc, bc) 

                                    # 事前に一部計算
                                    z_abc = zbab + zcac
                                    z_bca = zcbc + zaba
                                    z_acc = zcac*2
                                    z_bcc = zcbc*2
                                 
                                    # 各パターンについて計算して
                                    # 判定、相性値、各名前（子、親①、祖父①、祖母①、親②、祖父②、祖母②の順）でリストに結果を格納。
                                    # Z-ABC×BCA
                                    if st.session_state.check_ptn1:
                                        aff1 = aff_base + z_abc + z_bca 
                                        mark1 = get_mark(aff1)
                                        lis_affinities.append([mark1, aff1, name_z, name_a, name_b, name_c, name_b, name_c, name_a] )

                                    # Z-ACC×BCC
                                    if st.session_state.check_ptn2:
                                        aff2 = aff_base + z_acc + z_bcc 
                                        mark2 = get_mark(aff2)
                                        lis_affinities.append([mark2, aff2, name_z, name_a, name_c, name_c, name_b, name_c, name_c] )

                                    # Z-ABB×BCA, Z-ABC×BAA
                                    if st.session_state.check_ptn3:
                                        aff3_1 = aff_base + z_abb + z_bca 
                                        aff3_2 = aff_base + z_abc + z_baa 
                                        mark3_1 = get_mark(aff3_1)
                                        lis_affinities.append([mark3_1, aff3_1, name_z, name_a, name_b, name_b, name_b, name_c, name_a] )
                                        mark3_2 = get_mark(aff3_2)
                                        lis_affinities.append([mark3_2, aff3_2, name_z, name_a, name_b, name_c, name_b, name_a, name_a] ) 
                                    
                                    # Z-ABB×BCC, Z-ACC×BAA
                                    if st.session_state.check_ptn4:
                                        aff4_1 = aff_base + z_abb + z_bcc
                                        aff4_2 = aff_base + z_acc + z_baa
                                        mark4_1 = get_mark(aff4_1)
                                        lis_affinities.append([mark4_1, aff4_1, name_z, name_a, name_b, name_b, name_b, name_c, name_c] ) 
                                        mark4_2 = get_mark(aff4_2)
                                        lis_affinities.append([mark4_2, aff4_2, name_z, name_a, name_c, name_c, name_b, name_a, name_a] ) 

                                    # Z-ABC×BCC, Z-ACC×BCA
                                    if st.session_state.check_ptn5:
                                        aff5_1 = aff_base + z_abc + z_bcc
                                        aff5_2 = aff_base + z_acc + z_bca
                                        mark5_1 = get_mark(aff5_1)
                                        lis_affinities.append([mark5_1, aff5_1, name_z, name_a, name_b, name_c, name_b, name_c, name_c] ) 
                                        mark5_2 = get_mark(aff5_2)
                                        lis_affinities.append([mark5_2, aff5_2, name_z, name_a, name_c, name_c, name_b, name_c, name_a] )                            

                                    

                                    
    write_log(f"◎子-両親-祖父母①-祖父母②の組み合わせ：{len(lis_affinities):,}件")
    if len(lis_affinities) == 0:
        st.error(f"子-両親-祖父母①-祖父母②の組み合わせ候補が0件です。\n他の検索手法を利用してください。")
        return ret, df_affinities

    # データ整形
    df_affinities = shape_data(lis_affinities)

    # 返却値設定
    ret = True

    return ret, df_affinities



# 子のみ検索用(エラー処理などほとんど削除)
def calc_affinity_m_select(Monster_info, datalist):
    
    # 参照高速化のためにローカル設定
    lis_affinities_m_cp     = datalist.lis_affinities_m_cp
    lis_affinities_s_cp     = datalist.lis_affinities_s_cp
    lis_affinities_m_cpg    = datalist.lis_affinities_m_cpg
    lis_affinities_s_cpg    = datalist.lis_affinities_s_cpg
    lis_mons_league_tb_c    = st.session_state.session_datalist.lis_mons_league_tb_c
    df_monsters             = datalist.df_monsters
    # 保管用リストの作成
    lis_affinities      = []
    df_affinities       = pd.DataFrame( [] )
    lis_good_monsters   = []
    # 共通秘伝値事前計算
    common_aff = st.session_state.input_common_aff2 * DataList.common_aff2 + st.session_state.input_common_aff3 * DataList.common_aff3
    
    # 子-親-祖父-祖母のメイン/サブ血統(あり得ない組み合わせはスキップ)
    parent1_m = Monster_info[1].ped1_num[0]
    granpa1_m = Monster_info[2].ped1_num[0]
    granma1_m = Monster_info[3].ped1_num[0]
    parent1_s = Monster_info[1].ped2_num[0]
    granpa1_s = Monster_info[2].ped2_num[0]
    granma1_s = Monster_info[3].ped2_num[0]
    parent2_m = Monster_info[4].ped1_num[0]
    granpa2_m = Monster_info[5].ped1_num[0]
    granma2_m = Monster_info[6].ped1_num[0]
    parent2_s = Monster_info[4].ped2_num[0]
    granpa2_s = Monster_info[5].ped2_num[0]
    granma2_s = Monster_info[6].ped2_num[0]
    pp1 = lis_affinities_m_cp[ parent1_m ][ parent2_m ]
    pp2 = lis_affinities_s_cp[ parent1_s ][ parent2_s ]
    for child1 in Monster_info[0].ped1_num:
        cpg1_m = lis_affinities_m_cpg[child1][parent1_m][granpa1_m][granma1_m]
        cpg2_m = lis_affinities_m_cpg[child1][parent2_m][granpa2_m][granma2_m]
        for child2 in Monster_info[0].ped2_num:
            name_c = lis_mons_league_tb_c[child1][child2]
            if name_c == "-":
                continue
            cpg1_s = lis_affinities_s_cpg[child2][parent1_s][granpa1_s][granma1_s]
            cpg2_s = lis_affinities_s_cpg[child2][parent2_s][granpa2_s][granma2_s]
            cpg1 = cpg1_m + cpg1_s
            cpg2 = cpg2_m + cpg2_s
            pp = pp1 + pp2
            affinity = cpg1 + cpg2 + pp
            all_affinity = affinity + common_aff
            mark = get_mark(all_affinity)
            lis_affinities.append([mark, name_c, all_affinity, cpg1, cpg2, pp, affinity, common_aff])
            if all_affinity >= 475:
                lis_good_monsters.append(child1)

    # データ整形
    df_affinities = shape_data_select(lis_affinities)
    freq = collections.Counter(lis_good_monsters)
    str_good_monsters = ""
    for child in freq.most_common():
        if child[1] > 2:
            name = df_monsters[ df_monsters["主血統ID"] == child[0] ].iloc[0, 1]
            str_good_monsters += f"{name},　"
        else:
            break

    return df_affinities, str_good_monsters



# 子のみ検索用(エラー処理などほとんど削除)
def calc_affinity_m_s_select(Monster_info, datalist):

    # 参照高速化のためにローカル設定
    lis_affinities_m_s_cp   = datalist.lis_affinities_m_s_cp
    lis_affinities_m_cp     = datalist.lis_affinities_m_cp
    lis_affinities_s_cp     = datalist.lis_affinities_s_cp
    lis_mons_league_tb_c    = st.session_state.session_datalist.lis_mons_league_tb_c
    df_monsters             = datalist.df_monsters
    # 保管用リストの作成
    lis_affinities      = []
    df_affinities       = pd.DataFrame( [] )
    lis_good_monsters   = []
    # 共通秘伝値事前計算
    common_aff = st.session_state.input_common_aff2 * DataList.common_aff2 + st.session_state.input_common_aff3 * DataList.common_aff3

    # 変数に再格納
    parent1_m = Monster_info[1].ped1_num[0]
    parent1_s = Monster_info[1].ped2_num[0]
    granpa1_m = Monster_info[2].ped1_num[0]
    granpa1_s = Monster_info[2].ped2_num[0]
    granma1_m = Monster_info[3].ped1_num[0]
    granma1_s = Monster_info[3].ped2_num[0]
    parent2_m = Monster_info[4].ped1_num[0]
    parent2_s = Monster_info[4].ped2_num[0]
    granpa2_m = Monster_info[5].ped1_num[0]
    granpa2_s = Monster_info[5].ped2_num[0]
    granma2_m = Monster_info[6].ped1_num[0]
    granma2_s = Monster_info[6].ped2_num[0]
    pgp1 = lis_affinities_m_s_cp[parent1_m][parent1_s][granpa1_m][granpa1_s]
    pgm1 = lis_affinities_m_s_cp[parent1_m][parent1_s][granma1_m][granma1_s]
    pgp2 = lis_affinities_m_s_cp[parent2_m][parent2_s][granpa2_m][granpa2_s]
    pgm2 = lis_affinities_m_s_cp[parent2_m][parent2_s][granma2_m][granma2_s]
    pp1 = lis_affinities_m_cp[ parent1_m ][ parent2_m ]
    pp2 = lis_affinities_s_cp[ parent1_s ][ parent2_s ]

    # 子-親-祖父-祖母のメイン/サブ血統(あり得ない組み合わせはスキップ)
    for child_m in Monster_info[0].ped1_num:
        for child_s in Monster_info[0].ped2_num:
            name_c = lis_mons_league_tb_c[child_m][child_s]
            if name_c == "-":
                continue

            # 親①側
            cp1 = lis_affinities_m_s_cp[child_m][child_s][parent1_m][parent1_s]
            cg1_1 = lis_affinities_m_s_cp[child_m][child_s][granpa1_m][granpa1_s]
            cpg1_1 = min(cg1_1, pgp1)
            cg1_2 = lis_affinities_m_s_cp[child_m][child_s][granma1_m][granma1_s]
            cpg1_2 = min(cg1_2, pgm1)

            # 親②側
            cp2 = lis_affinities_m_s_cp[child_m][child_s][parent2_m][parent2_s]
            cg2_1 = lis_affinities_m_s_cp[child_m][child_s][granpa2_m][granpa2_s]
            cpg2_1 = min(cg2_1, pgp2)
            cg2_2 = lis_affinities_m_s_cp[child_m][child_s][granma2_m][granma2_s]
            cpg2_2 = min(cg2_2, pgm2)

            # 全体計算
            cpg1 = cp1 + cpg1_1 + cpg1_2
            cpg2 = cp2 + cpg2_1 + cpg2_2
            pp = pp1 + pp2
            affinity = cpg1 + cpg2 + pp
            all_affinity = affinity + common_aff
            mark = get_mark(all_affinity)

            # 格納
            lis_affinities.append([mark, name_c, all_affinity, cpg1, cpg2, pp, affinity, common_aff])
            if all_affinity >= 475:
                lis_good_monsters.append(child_m)

    # データ整形
    df_affinities = shape_data_select(lis_affinities)
    freq = collections.Counter(lis_good_monsters)
    str_good_monsters = ""
    for child in freq.most_common():
        if child[1] > 2:
            name = df_monsters[ df_monsters["主血統ID"] == child[0] ].iloc[0, 1]
            str_good_monsters += f"{name},　"
        else:
            break

    return df_affinities, str_good_monsters



# テスト用
def out_candidates(lis_search_mons_ids, datalist):

    # 返却値
    ret = False
    # 共通秘伝値事前計算
    common_aff = st.session_state.input_common_aff2 * DataList.common_aff2 + st.session_state.input_common_aff3 * DataList.common_aff3
    # 閾値
    THRESH1 = 37
    THRESH2 = 73
    # THRESH3 = 500 - common_aff - 32*7
    # THRESH3 = 205
    THRESH3 = 203

    # 参照高速化のためにローカル設定
    lis_affinities_m_cp     = datalist.lis_affinities_m_cp
    lis_affinities_m_cpg    = datalist.lis_affinities_m_cpg
    lis_affinities_m_cpg2   = datalist.lis_affinities_m_cpg2
    lis_mons_league_tb_pg   = st.session_state.session_datalist.lis_mons_league_tb_pg
    lis_affinities      = []
    df_affinities       = pd.DataFrame( [] )

    # 0件でないか確認。
    if len(lis_search_mons_ids) == 0:
        st.error(f"育成したい種族を1つ以上選択してから検索してください。\n")
        return ret, df_affinities
    
    # 親-親のリストを作成
    num_m_mons       = len(lis_mons_league_tb_pg)
    lis_good_parents = [0] * num_m_mons
    mons_id_list     = []
    for i in range(num_m_mons):
        if lis_mons_league_tb_pg[i][0] == "-":
            lis_good_parents[i] = []
        else:
            mons_id_list.append(i)

    for i in mons_id_list:
        lis_temp = []
        for j in mons_id_list:
            if THRESH1 <= lis_affinities_m_cp[i][j]:
                lis_temp.append(j)
        lis_good_parents[i] = lis_temp
    
    # 子→片親分の組合せを確認
    lis_p_g_id = [0]*(num_m_mons**3)
    lis_parents_index = [0] * num_m_mons
    i = 0
    for parent in mons_id_list:
        for granpa in mons_id_list:
            for granma in mons_id_list:
                if granma < granpa:
                    continue
                is_ok = True
                for child in mons_id_list:  # 上位からの子のリストを使用するべき。
                    if lis_affinities_m_cpg2[parent][granpa][granma][child] < THRESH2:
                        is_ok = False
                        break
                if is_ok:
                    lis_p_g_id[i] = [parent, granpa, granma]
                    i += 1
        lis_parents_index[parent] = i
    lis_p_g_id = lis_p_g_id[:i]  # サイズを調整
    
    # 子一人目だけを使用してループ処理を実施し、子以外のリストを作成する。
    p1 = 0
    pg_pairs = []
    child    = lis_search_mons_ids[0]
    for pg1 in lis_p_g_id:
        if pg1[0] != p1:
            # 親が変わったため、リストを変更する。
            p1 = pg1[0]
            lis_p_g_id2_idx = []
            for i in lis_good_parents[p1]:
                lis_temp = [j for j in range(lis_parents_index[i-1], lis_parents_index[i])]
                lis_p_g_id2_idx = lis_p_g_id2_idx + lis_temp  # 連結
        v_cpg1 = lis_affinities_m_cpg[child][pg1[0]][pg1[1]][pg1[2]]
        for pg2_i in lis_p_g_id2_idx:
            pg2    = lis_p_g_id[pg2_i]
            v_cpg2 = lis_affinities_m_cpg[child][pg2[0]][pg2[1]][pg2[2]]
            v_pp   = lis_affinities_m_cp[pg1[0]][pg2[0]]
            if (v_pp + v_cpg1 + v_cpg2) >= THRESH3:
                pg_pairs.append([pg1[0], pg1[1], pg1[2], pg2[0], pg2[1], pg2[2]])

    # 子2人目以降について、逆順でリストを参照して候補を削る。
    for i, child in enumerate(lis_search_mons_ids):
        if i == 0:
            continue
        cnt = 0
        while cnt < len(pg_pairs):
            pg_pair = pg_pairs[cnt]
            v_cpg1 = lis_affinities_m_cpg[child][pg_pair[0]][pg_pair[1]][pg_pair[2]]
            v_cpg2 = lis_affinities_m_cpg[child][pg_pair[3]][pg_pair[4]][pg_pair[5]]
            v_pp   = lis_affinities_m_cp[pg_pair[0]][pg_pair[3]]
            if (v_pp + v_cpg1 + v_cpg2) >= THRESH3:
                cnt += 1
            else:
                pg_pairs.pop(cnt)

    # 名前のリストに変換
    for pg_pair in pg_pairs:
        min_v = 5000
        for child in lis_search_mons_ids:
            v_cpg1 = lis_affinities_m_cpg[child][pg_pair[0]][pg_pair[1]][pg_pair[2]]
            v_cpg2 = lis_affinities_m_cpg[child][pg_pair[3]][pg_pair[4]][pg_pair[5]]
            v_pp   = lis_affinities_m_cp[pg_pair[0]][pg_pair[3]]
            val = v_cpg1 + v_cpg2 + v_pp
            if val < min_v:
                min_v = val
        min_v = min_v + 7*32 + common_aff
        p1  = lis_mons_league_tb_pg[pg_pair[0]][0]
        gp1 = lis_mons_league_tb_pg[pg_pair[1]][0]
        gm1 = lis_mons_league_tb_pg[pg_pair[2]][0]
        p2  = lis_mons_league_tb_pg[pg_pair[3]][0]
        gp2 = lis_mons_league_tb_pg[pg_pair[4]][0]
        gm2 = lis_mons_league_tb_pg[pg_pair[5]][0]
        mark = get_mark(min_v)
        lis_affinities.append([mark, min_v, "-", p1, gp1, gm1, p2, gp2, gm2])

    if len(lis_affinities) == 0:
        st.error(f"評価◎以上の子-両親-祖父母①-祖父母②の組み合わせ候補が0件です。\n現状の閾値設定では出力不可です。管理者に問い合わせください。\n")
        return ret, df_affinities

    # データ整形
    df_affinities = shape_data2(lis_affinities)

    # 最後に出力
    # print(len(df_affinities))

    # 返却値設定
    ret = True
 
    return ret, df_affinities

