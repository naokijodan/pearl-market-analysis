#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新しいカテゴリタブをメインHTMLに統合し、チェックボックス機能を追加
"""

import json
import re

# pearl_overview_analysis.jsonからオーバービューデータを読み込み
with open('/Users/naokijodan/Desktop/pearl_overview_analysis.json', 'r', encoding='utf-8') as f:
    overview_data = json.load(f)

# 新しいカテゴリタブHTMLを読み込み
with open('/Users/naokijodan/Desktop/pearl_category_tabs.html', 'r', encoding='utf-8') as f:
    category_tabs_html = f.read()

# チェックボックス用のCSS
checkbox_css = '''
        .search-checkbox {
            margin-left: 5px;
            margin-right: 10px;
            cursor: pointer;
            width: 16px;
            height: 16px;
            vertical-align: middle;
        }
        .brand-section {
            margin-bottom: 30px;
        }
'''

# チェックボックス用のJavaScript
checkbox_js = '''
        // チェックボックスのlocalStorage管理
        document.addEventListener('DOMContentLoaded', function() {
            // ページ読み込み時にチェック状態を復元
            const checkboxes = document.querySelectorAll('.search-checkbox');
            checkboxes.forEach(checkbox => {
                const checkboxId = checkbox.getAttribute('data-id');
                if (checkboxId) {
                    const isChecked = localStorage.getItem(`checkbox_${checkboxId}`) === 'true';
                    checkbox.checked = isChecked;
                }

                // チェックボックスの変更を監視
                checkbox.addEventListener('change', function() {
                    const checkboxId = this.getAttribute('data-id');
                    if (checkboxId) {
                        localStorage.setItem(`checkbox_${checkboxId}`, this.checked);
                    }
                });
            });
        });
'''

# ベースHTML構造を生成
html_template = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>パール市場データ分析</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f5f5f5;
            --bg-card: #ffffff;
            --text-primary: #212121;
            --text-secondary: #757575;
            --border-color: #e0e0e0;
            --accent: #E91E63;
            --success: #4CAF50;
            --warning: #FF9800;
        }}
        [data-theme="dark"] {{
            --bg-primary: #121212;
            --bg-secondary: #1e1e1e;
            --bg-card: #2d2d2d;
            --text-primary: #e0e0e0;
            --text-secondary: #9e9e9e;
            --border-color: #424242;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{
            background: var(--bg-card);
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .header-title {{ font-size: 1.5rem; font-weight: 700; }}
        .header-controls {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .btn-primary {{ background: var(--accent); color: white; }}
        .btn-primary:hover {{ opacity: 0.9; }}
        .btn-secondary {{ background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border-color); }}
        .input-group {{ display: flex; align-items: center; gap: 8px; }}
        .input-group label {{ font-size: 14px; color: var(--text-secondary); }}
        .input-group input {{
            width: 80px;
            padding: 6px 10px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            background: var(--bg-card);
            color: var(--text-primary);
        }}
        .tabs {{
            display: flex;
            gap: 4px;
            background: var(--bg-card);
            padding: 10px 20px;
            border-bottom: 1px solid var(--border-color);
            overflow-x: auto;
            flex-wrap: nowrap;
        }}
        .tab-btn {{
            padding: 10px 20px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 14px;
            border-radius: 6px;
            color: var(--text-secondary);
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{ background: var(--bg-secondary); }}
        .tab-btn.active {{ background: var(--accent); color: white; }}
        .tab-content {{ display: none; padding: 20px 0; }}
        .tab-content.active {{ display: block; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        .stat-card {{
            background: var(--bg-card);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .stat-card .label {{ font-size: 13px; color: var(--text-secondary); margin-bottom: 5px; }}
        .stat-card .value {{ font-size: 28px; font-weight: 700; }}
        .stat-card .sub {{ font-size: 12px; color: var(--text-secondary); margin-top: 5px; }}
        .table-container {{
            background: var(--bg-card);
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        .table-header {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .table-header h3 {{ font-size: 16px; }}
        .search-box {{
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            width: 250px;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--border-color); }}
        th {{ background: var(--bg-secondary); font-weight: 600; font-size: 13px; color: var(--text-secondary); }}
        tr:hover {{ background: var(--bg-secondary); }}
        .link-btn {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            text-decoration: none;
            color: white;
            margin-right: 4px;
        }}
        .link-mercari {{ background: #FF4B5C; }}
        .link-ebay {{ background: #0064D2; }}
{checkbox_css}
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .search-box {{ width: 100%; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-title">📿 パール市場データ分析</div>
        <div class="header-controls">
            <div class="input-group">
                <label>為替:</label>
                <input type="number" id="exchangeRate" value="155" onchange="updatePrices()">
                <span>円/$</span>
                <button class="btn btn-primary" onclick="fetchExchangeRate()">取得</button>
            </div>
            <div class="input-group">
                <label>送料:</label>
                <input type="number" id="shippingCost" value="3000" onchange="updatePrices()">
                <span>円</span>
            </div>
            <button class="btn btn-secondary" onclick="toggleTheme()">🌙 テーマ切替</button>
        </div>
    </header>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('overview')">📊 全体分析</button>
        <button class="tab-btn" onclick="switchTab('ネックレス')">📿 ネックレス</button>
        <button class="tab-btn" onclick="switchTab('イヤリング')">👂 イヤリング</button>
        <button class="tab-btn" onclick="switchTab('ブローチ')">🎀 ブローチ</button>
        <button class="tab-btn" onclick="switchTab('ブレスレット')">⛓️ ブレスレット</button>
        <button class="tab-btn" onclick="switchTab('その他')">✨ その他</button>
        <button class="tab-btn" onclick="switchTab('リング')">💎 リング</button>
        <button class="tab-btn" onclick="switchTab('ペンダント')">🔗 ペンダント</button>
    </div>

    <div class="container">
        <div id="tab-overview" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="label">総グループ数</div>
                    <div class="value">112</div>
                    <div class="sub">2件以上販売</div>
                </div>
                <div class="stat-card">
                    <div class="label">総販売数</div>
                    <div class="value">1,539</div>
                    <div class="sub">個</div>
                </div>
                <div class="stat-card">
                    <div class="label">カテゴリ数</div>
                    <div class="value">7</div>
                    <div class="sub">種類</div>
                </div>
                <div class="stat-card">
                    <div class="label">平均中央値</div>
                    <div class="value">$162</div>
                    <div class="sub">USD</div>
                </div>
            </div>

            <div class="info-banner" style="background: linear-gradient(135deg, #E91E63 0%, #9C27B0 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                <h3 style="margin-bottom: 10px;">💎 市場インサイト</h3>
                <p style="margin-bottom: 10px;"><strong>主要トレンド:</strong> ネックレスが908個（59.0%）で市場を牽引。CHANELとVivienne Westwoodが上位2ブランド。</p>
                <p style="margin-bottom: 10px;"><strong>価格帯分析:</strong> 中央値$162、最頻価格帯$101-200（高回転ゾーン）</p>
                <p><strong>推奨戦略:</strong> ①ネックレスは高回転カテゴリ - 在庫を厚めに ②CHANELは安定需要 - 仕入れルート確保 ③価格帯$150-200が主戦場</p>
            </div>

            <div class="charts-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 25px;">
                <div class="chart-card" style="background: var(--bg-card); padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <h3 style="font-size: 16px; margin-bottom: 15px;">カテゴリ別販売数</h3>
                    <div id="chart-category-sales"></div>
                </div>
                <div class="chart-card" style="background: var(--bg-card); padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <h3 style="font-size: 16px; margin-bottom: 15px;">カテゴリ別シェア</h3>
                    <div id="chart-category-pie"></div>
                </div>
                <div class="chart-card" style="background: var(--bg-card); padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <h3 style="font-size: 16px; margin-bottom: 15px;">ブランド別販売数 TOP10</h3>
                    <div id="chart-brand-sales"></div>
                </div>
                <div class="chart-card" style="background: var(--bg-card); padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <h3 style="font-size: 16px; margin-bottom: 15px;">価格帯分布</h3>
                    <div id="chart-price-dist"></div>
                </div>
                <div class="chart-card" style="background: var(--bg-card); padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <h3 style="font-size: 16px; margin-bottom: 15px;">素材クラス分布</h3>
                    <div id="chart-material"></div>
                </div>
                <div class="chart-card" style="background: var(--bg-card); padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <h3 style="font-size: 16px; margin-bottom: 15px;">人気モチーフ TOP10</h3>
                    <div id="chart-motif"></div>
                </div>
            </div>
        </div>

{category_tabs_html}
    </div>

    <script>
        // タブ切り替え
        function switchTab(tabName) {{
            const tabs = document.querySelectorAll('.tab-content');
            const tabBtns = document.querySelectorAll('.tab-btn');

            tabs.forEach(tab => tab.classList.remove('active'));
            tabBtns.forEach(btn => btn.classList.remove('active'));

            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        // テーマ切り替え
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? '' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }}

        // テーマを復元
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {{
            document.documentElement.setAttribute('data-theme', savedTheme);
        }}

        // テーブル検索フィルター
        function filterTable(input, tableId) {{
            const filter = input.value.toLowerCase();
            const table = document.getElementById(tableId);
            const rows = table.getElementsByTagName('tr');

            for (let i = 1; i < rows.length; i++) {{
                const row = rows[i];
                const text = row.textContent || row.innerText;
                if (text.toLowerCase().indexOf(filter) > -1) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }}
        }}

        // 為替レート取得
        async function fetchExchangeRate() {{
            try {{
                const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
                const data = await response.json();
                const rate = data.rates.JPY;
                document.getElementById('exchangeRate').value = Math.round(rate);
                updatePrices();
                alert(`為替レートを更新しました: $1 = ¥${{Math.round(rate)}}`);
            }} catch (error) {{
                alert('為替レートの取得に失敗しました');
            }}
        }}

        // 価格更新
        function updatePrices() {{
            const rate = parseFloat(document.getElementById('exchangeRate').value);
            const shipping = parseFloat(document.getElementById('shippingCost').value);
            const fee = 0.2;

            document.querySelectorAll('.price-jpy').forEach(el => {{
                const priceMatch = el.textContent.match(/([\\d,]+)/);
                if (priceMatch) {{
                    const originalPrice = parseFloat(priceMatch[1].replace(/,/g, ''));
                    const usdPrice = originalPrice / 155;
                    const newPrice = Math.round(usdPrice * rate);
                    el.textContent = `¥${{newPrice.toLocaleString()}}`;
                }}
            }});

            document.querySelectorAll('.price-breakeven').forEach(el => {{
                const priceMatch = el.textContent.match(/([\\d,]+)/);
                if (priceMatch) {{
                    const originalPrice = parseFloat(priceMatch[1].replace(/,/g, ''));
                    const usdPrice = originalPrice / 155;
                    const jpy = usdPrice * rate;
                    const breakeven = Math.round(((jpy + shipping) / (1 - fee)) * 0.8);
                    el.textContent = `¥${{breakeven.toLocaleString()}}`;
                }}
            }});
        }}

{checkbox_js}

        // Overview charts data
        const overviewData = {json.dumps(overview_data, ensure_ascii=False, indent=12)};

        // カテゴリ別販売数チャート
        Plotly.newPlot('chart-category-sales', [{{
            x: Object.keys(overviewData.category_sales),
            y: Object.values(overviewData.category_sales),
            type: 'bar',
            marker: {{ color: '#E91E63' }}
        }}], {{
            title: '',
            xaxis: {{ title: '' }},
            yaxis: {{ title: '販売数' }},
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: {{ t: 20, r: 20, b: 60, l: 60 }}
        }}, {{ responsive: true }});

        // カテゴリ別シェア円グラフ
        Plotly.newPlot('chart-category-pie', [{{
            labels: Object.keys(overviewData.category_sales),
            values: Object.values(overviewData.category_sales),
            type: 'pie',
            marker: {{ colors: ['#E91E63', '#9C27B0', '#3F51B5', '#00BCD4', '#4CAF50', '#FF9800', '#795548'] }}
        }}], {{
            title: '',
            paper_bgcolor: 'rgba(0,0,0,0)',
            margin: {{ t: 20, r: 20, b: 20, l: 20 }}
        }}, {{ responsive: true }});

        // ブランド別販売数チャート（TOP10）
        const brandEntries = Object.entries(overviewData.brand_sales).slice(0, 10);
        Plotly.newPlot('chart-brand-sales', [{{
            x: brandEntries.map(e => e[0]),
            y: brandEntries.map(e => e[1]),
            type: 'bar',
            marker: {{ color: '#9C27B0' }}
        }}], {{
            title: '',
            xaxis: {{ title: '', tickangle: -45 }},
            yaxis: {{ title: '販売数' }},
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: {{ t: 20, r: 20, b: 100, l: 60 }}
        }}, {{ responsive: true }});

        // 価格帯分布チャート
        Plotly.newPlot('chart-price-dist', [{{
            x: Object.keys(overviewData.price_ranges),
            y: Object.values(overviewData.price_ranges),
            type: 'bar',
            marker: {{ color: '#3F51B5' }}
        }}], {{
            title: '',
            xaxis: {{ title: '価格帯' }},
            yaxis: {{ title: '販売数' }},
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: {{ t: 20, r: 20, b: 60, l: 60 }}
        }}, {{ responsive: true }});

        // 素材クラス分布チャート
        Plotly.newPlot('chart-material', [{{
            labels: Object.keys(overviewData.material_sales),
            values: Object.values(overviewData.material_sales),
            type: 'pie',
            marker: {{ colors: ['#00BCD4', '#9E9E9E', '#4CAF50'] }}
        }}], {{
            title: '',
            paper_bgcolor: 'rgba(0,0,0,0)',
            margin: {{ t: 20, r: 20, b: 20, l: 20 }}
        }}, {{ responsive: true }});

        // 人気モチーフチャート（TOP10）
        const motifEntries = Object.entries(overviewData.motif_sales).slice(0, 10);
        Plotly.newPlot('chart-motif', [{{
            x: motifEntries.map(e => e[0]),
            y: motifEntries.map(e => e[1]),
            type: 'bar',
            marker: {{ color: '#FF9800' }}
        }}], {{
            title: '',
            xaxis: {{ title: '', tickangle: -45 }},
            yaxis: {{ title: '販売数' }},
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: {{ t: 20, r: 20, b: 80, l: 60 }}
        }}, {{ responsive: true }});
    </script>
</body>
</html>
'''

# 最終HTMLを保存
output_file = '/Users/naokijodan/Desktop/パール市場データ_統合版_2026-01-28.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"✅ 最終HTML生成完了: {output_file}")
print(f"📊 総文字数: {len(html_template):,} 文字")
