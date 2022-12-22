cols = ["mfr", "name", "type", # Common Identifier
    "mdl", "gen", "grade", # Additional Identifier
    "mfr_year", "mdl_year", # Years
    "price", "kmpl", "fuel", # Cost
    "tax", "w_tax", "mand_ins", "oil_chg", "tire_chg", "opt_ins", "preloan_cst", "pstloan_cst", "insp_cst", # Maintenance
    "doors", "psngrs", # Capacity
    "ext_l", "ext_w", "ext_h", "int_l", "int_w", "int_h", # Dimensions
    "w_base", "w_track_f", "w_track_r", "grnd_clr", # Terrain Related Dimensions
    "turn_rad", # minimum turn radius
    "weight", # Weight
    "drive", "gears", "trans", # Driving Characteristics
    "eng_mdl", "eng_layout", "cc", "comp_ratio", "comp_type", "kw", "kw_rpm", "trq_nm", "trq_rpm", # Engine Specs
    "w_w_f", "w_ratio_f", "w_cnst_f", "w_rim_f", "w_w_r", "w_ratio_r", "w_cnst_r", "w_rim_r", # Tire Dimensions and Construction
    "brake_f", "brake_r", # Brake Types
"car_link", "img_link"] # Misc

jp_cols = ["メーカー名", "車名", "車タイプ", # 一般識別
    "型式", "世代", "グレード", # 詳細識別
    "初販売年月", "モデル年式", # 年
    "価格", "燃費(km/l)", "使用燃料", # 一般費用
    "自動車税(1年)", "自動車重量税(1年)", "自賠責保険料(1年)", "オイル交換費(5000km毎)", "タイヤ交換費(5年5万km毎)", "任意保険料(1年)", "年間維持費(ローン返済中)", "年間維持費(ローン完済後)", "車検費用費", # 維持費
    "ドア数", "定員数", # 定員
    "車体長", "車体幅", "車体高", "室内長", "室内幅", "室内高", # 寸法
    "軸幅", "輪距(前)", "輪距(後)", "最低地上高", # 地形走破性関連寸法
    "最小回転半径", # 小回り
    "車重", # 重さ
    "ドライブ", "ギア数", "変速機", # ドライブ特徴
    "原動機型式", "気筒配列", "排気量", "圧縮比", "吸気方式", "最高出力(kW)", "最高出力回転数(rpm)", "最大トルク(Nm)", "最大トルク回転数(rpm)", # エンジンスペック
    "タイヤ幅(前)", "タイヤ比率(前)", "タイヤ構造(前)", "リム径(前)", "タイヤ幅(後)", "タイヤ比率(後)", "タイヤ構造(後)", "リム径(後)", # タイヤ寸法と構造
    "ブレーキ(前)", "ブレーキ(後)", # ブレーキタイプ
"参照元url", "車画像url"] # その他
