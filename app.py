#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify
import json

app = Flask(__name__)

# Загружаем рецепты
with open('recipes.json', 'r', encoding='utf-8') as f:
    RECIPES = json.load(f)

# Собираем уникальные ингредиенты
all_ingredients = set()
for recipe in RECIPES:
    for ing in recipe.get('ingredients', []):
        all_ingredients.add(ing.lower().strip())

# Группируем по категориям
categories = {
    "🥬 Овощи, зелень": [],
    "🥛 Молочные, яйца": [],
    "🍗 Мясо, колбаса": [],
    "🌾 Мука, крупы, бакалея": [],
    "🧂 Специи, масло, прочее": []
}

for ing in sorted(all_ingredients):
    if any(x in ing for x in ['кабачк', 'помидор', 'картошк', 'лук', 'морков', 'капуст', 'перец', 'яблок', 'чеснок', 'зелень', 'петрушк', 'укроп', 'кабачки']):
        categories["🥬 Овощи, зелень"].append(ing)
    elif any(x in ing for x in ['яйц', 'молоко', 'творог', 'сметан', 'сыр', 'масло сливоч', 'кефир']):
        categories["🥛 Молочные, яйца"].append(ing)
    elif any(x in ing for x in ['колбас', 'курин', 'курица', 'фарш', 'бекон', 'сосиск']):
        categories["🍗 Мясо, колбаса"].append(ing)
    elif any(x in ing for x in ['мука', 'сахар', 'рис', 'гречк', 'макарон', 'манк', 'разрыхлитель', 'сода', 'ванилин', 'дрожжи', 'пшеничная']):
        categories["🌾 Мука, крупы, бакалея"].append(ing)
    else:
        categories["🧂 Специи, масло, прочее"].append(ing)

# Убираем пустые категории
categories = {k: v for k, v in categories.items() if v}

HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Refrigerator Chef</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            background-image: url("/static/bg.jpg");
            background-repeat: no-repeat;
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: #2c2b28;
            padding: 20px 16px 40px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            font-size: 2.2rem;
            background: rgba(60, 94, 43, 0.85);
            -webkit-background-clip: text;
            background-clip: text;
            color: #fef9e8;
            display: inline-block;
            padding: 8px 24px;
            border-radius: 60px;
            backdrop-filter: blur(4px);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .sub { 
            color: #6b4c2c; margin-top: 6px;
            margin-top: 6px
            font-weight: 500;
            background: rgba(255, 255, 255, 0.85);
            display: inline-block;
            padding: 6px 20px;
            border-radius: 40px;
            backdrop-filter: blur(4px);
        }

        .stats-bar {
            display: flex;
            justify-content: space-between;
            margin: 16px 0 12px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .selected-count {
            background: #e9e0d0;
            padding: 6px 12px;
            border-radius: 40px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .reset-btn {
            background: #ffffff;
            border: 1px solid #d4c2a5;
            padding: 6px 16px;
            border-radius: 40px;
            cursor: pointer;
            font-size: 0.85rem;
            
        }
        .reset-btn:hover { background: #e9e0d0; }
        .category {
            background: white;
            border-radius: 28px;
            padding: 12px;
            margin-bottom: 20px;
            border: 1px solid #f0e2d0;
        }
        .category-title {
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 10px;
            color: #4a6741;
        }
        .ingredients-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .ingredient-btn {
            background: #f6f0e6;
            border: none;
            padding: 8px 18px;
            border-radius: 60px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: 0.2s;
        }
        .ingredient-btn.active {
            background: #e68a2e;
            color: white;
        }
        .ingredient-btn:hover { background: #e1d5c4; }
        .results-header {
            margin: 32px 0 16px 0;
            font-size: 1.5rem;
            font-weight: 600;
            border-left: 5px solid #e68a2e;
            padding-left: 16px;
        }
        .recipes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }
        .recipe-card {
            background: white;
            border-radius: 28px;
            padding: 18px;
            border: 1px solid #f1e2d2;
        }
        .recipe-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .recipe-time {
            display: inline-block;
            background: #f4ede4;
            padding: 4px 10px;
            border-radius: 30px;
            font-size: 0.75rem;
            margin-bottom: 12px;
        }
        .ingredients-list {
            margin: 12px 0;
            background: #fefaf5;
            padding: 12px;
            border-radius: 20px;
        }
        .ingredient-badge {
            display: inline-block;
            background: #e9e0d0;
            border-radius: 20px;
            padding: 4px 10px;
            margin: 4px 5px 0 0;
            font-size: 0.75rem;
        }
        .ingredient-badge.missing {
            background: #ffddd6;
            color: #b13e2d;
            text-decoration: line-through;
        }
        .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 16px;
        }
        .btn-instruction {
            background: #e68a2e;
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 60px;
            cursor: pointer;
            font-size: 0.8rem;
        }
        .btn-video {
            background: #2c3e66;
            color: white;
            text-decoration: none;
            padding: 8px 14px;
            border-radius: 60px;
            font-size: 0.8rem;
            display: inline-block;
        }
        .btn-link {
            color: #a55c1a;
            text-decoration: none;
            font-size: 0.75rem;
            border-bottom: 1px dashed #d4b48c;
        }
        .instruction-text {
            margin-top: 16px;
            background: #faf5ea;
            padding: 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            white-space: pre-wrap;
            display: none;
        }
        .instruction-text.show { display: block; }
        .empty-state {
            text-align: center;
            padding: 48px 20px;
            background: #fff6ea;
            border-radius: 48px;
            color: #9b7c5c;
        }
        footer {
            text-align: center;
            margin-top: 48px;
            font-size: 0.7rem;
            color: #aa8c6a;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🥘 Refrigerator Chef</h1>
        <div class="sub">шеф по тому, что есть в холодильнике</div>
    </div>
    <div class="stats-bar">
        <div class="selected-count" id="selectedCounter">✅ выбрано: 0 продуктов</div>
        <button class="reset-btn" id="resetBtn">🗑️ сбросить всё</button>
    </div>

    <div id="categoriesContainer"></div>

    <div class="results-header">🍽️ что можно приготовить</div>
    <div id="recipesContainer" class="recipes-grid"></div>
    <footer>Refrigerator Chef — выбери продукты, получи рецепты с учётом недостающих ингредиентов</footer>
</div>

<script>
    const RECIPES = {{ recipes|tojson }};
    const CATEGORIES = {{ categories|tojson }};
    
    let selectedIngredients = new Set();

    function renderIngredients() {
        let html = '';
        for (const [category, items] of Object.entries(CATEGORIES)) {
            html += '<div class="category"><div class="category-title">' + category + '</div><div class="ingredients-grid">';
            for (let i = 0; i < items.length; i++) {
                const ing = items[i];
                const active = selectedIngredients.has(ing) ? 'active' : '';
                html += '<button class="ingredient-btn ' + active + '" data-ingredient="' + ing.replace(/"/g, '&quot;') + '">' + ing + '</button>';
            }
            html += '</div></div>';
        }
        document.getElementById('categoriesContainer').innerHTML = html;
        
        document.querySelectorAll('.ingredient-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const ing = btn.getAttribute('data-ingredient');
                if (selectedIngredients.has(ing)) {
                    selectedIngredients.delete(ing);
                } else {
                    selectedIngredients.add(ing);
                }
                renderIngredients();
                renderRecipes();
                updateCounter();
            });
        });
    }

    function updateCounter() {
        document.getElementById('selectedCounter').innerText = '✅ выбрано: ' + selectedIngredients.size + ' продуктов';
    }

    function renderRecipes() {
        const container = document.getElementById('recipesContainer');
        const results = [];
        
        for (let r = 0; r < RECIPES.length; r++) {
            const recipe = RECIPES[r];
            const recipeIngs = [];
            for (let i = 0; i < recipe.ingredients.length; i++) {
                recipeIngs.push(recipe.ingredients[i].toLowerCase().trim());
            }
            const missing = [];
            for (let i = 0; i < recipeIngs.length; i++) {
                if (!selectedIngredients.has(recipeIngs[i])) {
                    missing.push(recipeIngs[i]);
                }
            }
            if (missing.length <= 2) {
                results.push({
                    title: recipe.title,
                    ingredients: recipe.ingredients,
                    instructions: recipe.instructions,
                    video: recipe.video,
                    link: recipe.link,
                    time: recipe.time,
                    missing: missing,
                    matchPercent: recipeIngs.length === 0 ? 0 : (recipeIngs.length - missing.length) / recipeIngs.length
                });
            }
        }
        
        results.sort(function(a, b) {
            if (a.missing.length !== b.missing.length) {
                return a.missing.length - b.missing.length;
            }
            return b.matchPercent - a.matchPercent;
        });
        
        if (results.length === 0) {
            container.innerHTML = '<div class="empty-state">😕 Ничего не найдено. Выберите больше продуктов.</div>';
            return;
        }
        
        let html = '';
        for (let idx = 0; idx < results.length; idx++) {
            const recipe = results[idx];
            const missingSet = new Set();
            for (let m = 0; m < recipe.missing.length; m++) {
                missingSet.add(recipe.missing[m]);
            }
            
            let ingHtml = '<div class="ingredients-list">📋 Ингредиенты:<br>';
            for (let i = 0; i < recipe.ingredients.length; i++) {
                const ing = recipe.ingredients[i];
                const isMissing = missingSet.has(ing.toLowerCase().trim());
                ingHtml += '<span class="ingredient-badge ' + (isMissing ? 'missing' : '') + '">' + ing + (isMissing ? ' (нет)' : ' ✓') + '</span>';
            }
            ingHtml += '</div>';
            
            const videoHtml = recipe.video ? '<a href="' + recipe.video + '" target="_blank" class="btn-video">🎬 Смотреть видео</a>' : '';
            const timeHtml = recipe.time ? '<span class="recipe-time">⏱️ ' + recipe.time + ' мин</span>' : '';
            const missingText = recipe.missing.length > 0 ? '<div style="font-size:0.75rem; color:#b13e2d; margin-bottom:12px;">⚠️ Не хватает: ' + recipe.missing.join(', ') + '</div>' : '<div style="font-size:0.75rem; color:#2f6b2f; margin-bottom:12px;">✅ У вас есть всё!</div>';
            
            const instrId = 'instr-' + idx;
            html += '<div class="recipe-card">';
            html += '<div class="recipe-title">' + recipe.title + '</div>';
            html += timeHtml;
            html += ingHtml;
            html += missingText;
            html += '<div class="actions">';
            html += '<button class="btn-instruction" data-idx="' + idx + '">📖 Показать инструкцию</button>';
            html += videoHtml;
            html += '<a href="' + recipe.link + '" target="_blank" class="btn-link">🔗 Оригинал</a>';
            html += '</div>';
            html += '<div id="' + instrId + '" class="instruction-text">' + (recipe.instructions || 'Инструкция не добавлена').replace(/\\n/g, '<br>') + '</div>';
            html += '</div>';
        }
        container.innerHTML = html;
        
        for (let idx = 0; idx < results.length; idx++) {
            const btn = document.querySelector('.btn-instruction[data-idx="' + idx + '"]');
            if (btn) {
                btn.addEventListener('click', function() {
                    const div = document.getElementById('instr-' + idx);
                    if (div.classList.contains('show')) {
                        div.classList.remove('show');
                        btn.innerText = '📖 Показать инструкцию';
                    } else {
                        div.classList.add('show');
                        btn.innerText = '📖 Скрыть инструкцию';
                    }
                });
            }
        }
    }

    document.getElementById('resetBtn').addEventListener('click', function() {
        selectedIngredients.clear();
        renderIngredients();
        renderRecipes();
        updateCounter();
    });

    renderIngredients();
    renderRecipes();
    updateCounter();
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML, recipes=RECIPES, categories=categories)

if __name__ == '__main__':
    print("\n🔥 Refrigerator Chef запущен!")
    print("👉 Откройте в браузере: http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=True)