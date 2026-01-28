#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カテゴリタブを新しい構造で再生成するスクリプト
- ブランドランキング表
- ブランド詳細セクション（モチーフ/素材/金属色別）
- eBay + メルカリの2リンクのみ + チェックボックス
"""

import json
import sys
from urllib.parse import quote

# JSONファイルを読み込む
with open('/Users/naokijodan/Desktop/pearl_hierarchical.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# カテゴリ名のマッピング
category_icons = {
    'ネックレス': '📿',
    'イヤリング': '👂',
    'ブローチ': '🎀',
    'ブレスレット': '⛓️',
    'その他': '✨',
    'リング': '💎',
    'ペンダント': '🔗',
    'ピアス': '💫'
}

def generate_brand_ranking_table(category_name, brands_ranking):
    """ブランドランキング表を生成"""
    if not brands_ranking:
        return ""

    html = f'''
            <div class="table-container" style="margin-bottom: 30px;">
                <div class="table-header">
                    <h3>{category_icons.get(category_name, '📦')} {category_name} - ブランド別ランキング</h3>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>順位</th>
                            <th>ブランド</th>
                            <th>総販売数</th>
                            <th>中央値(USD)</th>
                            <th>中央値(円)</th>
                            <th>仕入上限</th>
                        </tr>
                    </thead>
                    <tbody>
'''

    for idx, brand_info in enumerate(brands_ranking, 1):
        jp_brand = brand_info['jp_brand']
        total_sales = brand_info['total_sales']
        median = brand_info['median']
        jpy_median = brand_info['jpy_median']
        breakeven = brand_info['breakeven']

        html += f'''                        <tr>
                            <td>{idx}</td>
                            <td><strong>{jp_brand}</strong></td>
                            <td>{total_sales}</td>
                            <td>${median:.2f}</td>
                            <td class="price-jpy">¥{jpy_median:,}</td>
                            <td class="price-breakeven">¥{breakeven:,}</td>
                        </tr>
'''

    html += '''                    </tbody>
                </table>
            </div>
'''
    return html

def generate_ebay_link(category, brand, motif, material):
    """eBay検索リンクを生成"""
    # キーワード構築
    keywords = []
    if brand and brand != "(不明)":
        keywords.append(brand)
    keywords.append("pearl")
    keywords.append(category)

    search_query = " ".join(keywords)
    encoded_query = quote(search_query)

    return f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}&LH_Sold=1&LH_Complete=1"

def generate_mercari_link(jp_brand, category, motif, material):
    """メルカリ検索リンクを生成"""
    keywords = []

    if jp_brand and jp_brand != "(不明)":
        keywords.append(jp_brand)
    keywords.append(category)

    # モチーフと素材を追加（有効な場合のみ）
    if motif and motif != "-":
        keywords.append(motif)
    if material and material != "不明":
        keywords.append(material)

    search_query = " ".join(keywords)
    encoded_query = quote(search_query)

    return f"https://jp.mercari.com/search?keyword={encoded_query}&status=on_sale"

def generate_checkbox_id(category, jp_brand, motif, material, platform):
    """チェックボックスIDを生成"""
    # シンプルなID生成（英数字のみ）
    safe_category = category.replace(' ', '_')
    safe_brand = jp_brand.replace(' ', '_').replace('&', 'and')
    safe_motif = motif.replace(' ', '_') if motif and motif != '-' else 'none'
    safe_material = material.replace(' ', '_') if material and material != '不明' else 'unknown'

    return f"pearl_{safe_category}_{safe_brand}_{safe_motif}_{safe_material}_{platform}"

def generate_brand_detail_section(category_name, brand_name, details):
    """ブランド詳細セクションを生成"""
    if not details:
        return ""

    # ブランド名の英語表記を取得
    brand_en = details[0].get('brand', brand_name) if details else brand_name

    html = f'''
            <div class="brand-section" style="margin-bottom: 30px;">
                <h3 style="background: linear-gradient(135deg, #E91E63 0%, #9C27B0 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    {brand_name}の詳細分析
                </h3>

                <div class="table-container">
                    <div class="table-header">
                        <h3>モチーフ・素材・金属色別の販売データ</h3>
                        <input type="text" class="search-box" placeholder="検索..." onkeyup="filterTable(this, 'brand-{category_name}-{brand_name}-table')">
                    </div>
                    <table id="brand-{category_name}-{brand_name}-table">
                        <thead>
                            <tr>
                                <th>モチーフ</th>
                                <th>素材</th>
                                <th>金属色</th>
                                <th>販売数</th>
                                <th>eBay価格</th>
                                <th>中央値(円)</th>
                                <th>仕入上限</th>
                                <th>検索リンク</th>
                            </tr>
                        </thead>
                        <tbody>
'''

    for detail in details:
        motif = detail['motif']
        material = detail['material']
        metal_color = detail['metal_color']
        count = detail['count']
        min_price = detail['min']
        max_price = detail['max']
        median = detail['median']
        jpy = detail['jpy']
        breakeven = detail['breakeven']

        # リンク生成
        ebay_link = generate_ebay_link(category_name, brand_en, motif, material)
        mercari_link = generate_mercari_link(brand_name, category_name, motif, material)

        # チェックボックスID生成
        checkbox_ebay_id = generate_checkbox_id(category_name, brand_name, motif, material, 'ebay')
        checkbox_mercari_id = generate_checkbox_id(category_name, brand_name, motif, material, 'mercari')

        html += f'''                            <tr>
                                <td>{motif}</td>
                                <td>{material}</td>
                                <td>{metal_color}</td>
                                <td>{count}</td>
                                <td>${min_price:.2f}〜${max_price:.2f}</td>
                                <td class="price-jpy">¥{jpy:,}</td>
                                <td class="price-breakeven">¥{breakeven:,}</td>
                                <td>
                                    <a href="{ebay_link}" class="link-btn link-ebay" target="_blank">eBay</a>
                                    <input type="checkbox" class="search-checkbox" data-id="{checkbox_ebay_id}">
                                    <a href="{mercari_link}" class="link-btn link-mercari" target="_blank">メルカリ</a>
                                    <input type="checkbox" class="search-checkbox" data-id="{checkbox_mercari_id}">
                                </td>
                            </tr>
'''

    html += '''                        </tbody>
                    </table>
                </div>
            </div>
'''
    return html

def generate_category_tab(category_name, category_data):
    """カテゴリタブ全体を生成"""
    brands_ranking = category_data.get('brands_ranking', [])
    brands_detail = category_data.get('brands_detail', {})

    if not brands_ranking:
        return ""

    # 統計情報を計算
    total_sales = sum(b['total_sales'] for b in brands_ranking)
    num_brands = len(brands_ranking)
    total_groups = sum(len(details) for details in brands_detail.values())
    median_prices = [b['median'] for b in brands_ranking if b['median']]
    avg_median = sum(median_prices) / len(median_prices) if median_prices else 0

    html = f'''
        <div id="tab-{category_name}" class="tab-content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="label">販売数</div>
                    <div class="value">{total_sales:,}</div>
                    <div class="sub">個</div>
                </div>
                <div class="stat-card">
                    <div class="label">ブランド数</div>
                    <div class="value">{num_brands}</div>
                    <div class="sub">種類</div>
                </div>
                <div class="stat-card">
                    <div class="label">詳細グループ数</div>
                    <div class="value">{total_groups}</div>
                    <div class="sub">種類</div>
                </div>
                <div class="stat-card">
                    <div class="label">平均中央値</div>
                    <div class="value">${avg_median:.0f}</div>
                    <div class="sub">USD</div>
                </div>
            </div>
'''

    # ブランドランキング表を追加
    html += generate_brand_ranking_table(category_name, brands_ranking)

    # 各ブランドの詳細セクションを追加
    for brand_name, details in brands_detail.items():
        if details:  # 空でない場合のみ
            html += generate_brand_detail_section(category_name, brand_name, details)

    html += '''        </div>
'''
    return html

# すべてのカテゴリタブを生成
category_tabs_html = ""
for category_name in ['ネックレス', 'イヤリング', 'ブローチ', 'ブレスレット', 'その他', 'リング', 'ペンダント', 'ピアス']:
    if category_name in data:
        category_tabs_html += generate_category_tab(category_name, data[category_name])

# 結果をファイルに保存
output_file = '/Users/naokijodan/Desktop/pearl_category_tabs.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(category_tabs_html)

print(f"カテゴリタブHTMLを生成しました: {output_file}")
print(f"生成されたHTML: {len(category_tabs_html)} 文字")
