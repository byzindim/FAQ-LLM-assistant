"""A/B-тест промптов для FAQ-ассистента."""

import json
import time
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.abspath("."))

from app.llm.ollama_client import ask_ollama_sync
from app.prompts.base import ZERO_SHOT_TEMPLATE, FEW_SHOT_TEMPLATE, COT_TEMPLATE


def load_context() -> str:
    """Загружает все файлы базы знаний."""
    context = ""
    for fname in ["hr.md", "it_access.md", "equipment.md"]:
        path = f"app/knowledge_base/{fname}"
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                context += f.read() + "\n"
        else:
            print(f"⚠️ Файл {fname} не найден")
    return context


def is_correct(answer: str, expected: str) -> bool:
    """Простая проверка: есть ли ключевые слова из expected в ответе."""
    answer_low = answer.lower()
    keywords = [w for w in expected.lower().split() if len(w) > 3]
    
    if not keywords:
        return expected.lower() in answer_low
    
    matches = sum(1 for k in keywords if k in answer_low)
    return matches / len(keywords) >= 0.5


def test_prompt(template_name: str, template: str, dataset: list, context: str) -> dict:
    """Тестирует один тип промпта на всём датасете."""
    correct = 0
    total_time = 0
    
    print(f"\n{'='*60}")
    print(f"🧪 Тестируем: {template_name}")
    print(f"{'='*60}\n")
    
    for i, item in enumerate(dataset, 1):
        start = time.time()
        
        prompt = template.format(
            context=context,
            question=item["question"]
        )
        
        try:
            answer = ask_ollama_sync(prompt)
        except Exception as e:
            print(f"{i:2d}. ❌ Ошибка: {e}")
            elapsed = time.time() - start
            total_time += elapsed
            continue
        
        elapsed = time.time() - start
        total_time += elapsed
        
        is_ok = is_correct(answer, item["expected"])
        if is_ok:
            correct += 1
        
        status = "✅" if is_ok else "❌"
        print(f"{i:2d}. {status} [{elapsed:4.1f}s] Q: {item['question'][:45]}")
    
    accuracy = correct / len(dataset) * 100
    avg_time = total_time / len(dataset)
    
    print(f"\n📊 Результат {template_name}:")
    print(f"   🎯 Точность: {accuracy:.1f}% ({correct}/{len(dataset)})")
    print(f"   ⏱  Среднее время: {avg_time:.1f}s\n")
    
    return {
        "name": template_name,
        "accuracy": accuracy,
        "correct": correct,
        "total": len(dataset),
        "avg_time": avg_time
    }


def run_ab_test():
    """Запускает A/B-тест всех типов промптов."""
    with open("app/evaluation/dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    context = load_context()
    
    if not context:
        print("❌ База знаний пуста!")
        return
    
    print(f"📚 Загружено {len(context)} символов контекста")
    print(f"📋 Датасет: {len(dataset)} вопросов\n")
    
    templates = {
        "zero-shot": ZERO_SHOT_TEMPLATE,
        "few-shot": FEW_SHOT_TEMPLATE,
        "cot": COT_TEMPLATE,
    }
    
    results = []
    for name, template in templates.items():
        result = test_prompt(name, template, dataset, context)
        results.append(result)
    
    # Сохраняем результаты
    with open("METRICS.md", "w", encoding="utf-8") as f:
        f.write("# Метрики A/B-тестов промптов\n\n")
        f.write("## Сравнение методов\n\n")
        f.write("| Метод | Точность | Правильных | Среднее время |\n")
        f.write("|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['name']} | {r['accuracy']:.1f}% | {r['correct']}/{r['total']} | {r['avg_time']:.1f}s |\n")
        
        best = max(results, key=lambda x: x['accuracy'])
        f.write(f"\n## Вывод\n\n")
        f.write(f"**Лучший метод:** `{best['name']}` с точностью **{best['accuracy']:.1f}%**\n")
    
    # Финальная таблица
    print("\n" + "="*60)
    print("📊 ИТОГОВАЯ ТАБЛИЦА")
    print("="*60)
    print(f"{'Метод':<15} {'Точность':<12} {'Правильных':<12} {'Время':<10}")
    print("-"*60)
    for r in results:
        print(f"{r['name']:<15} {r['accuracy']:>6.1f}%      {r['correct']:>2}/{r['total']:<8} {r['avg_time']:>5.1f}s")
    
    print(f"\n✅ Результаты сохранены в METRICS.md")


if __name__ == "__main__":
    run_ab_test()
