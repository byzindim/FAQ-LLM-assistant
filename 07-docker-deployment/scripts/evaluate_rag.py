import sys
import asyncio
import nest_asyncio
import json
import time
import httpx
import re
nest_asyncio.apply()

sys.path.insert(0, '/content')

from app.prompts.base import JUDGE_TEMPLATE

async def evaluate_dataset():
    # 1. Загружаем датасет
    dataset_path = '/content/app/evaluation/dataset.json'
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print(f"❌ Датасет не найден: {dataset_path}")
        return
    
    print(f"📊 Starting evaluation on {len(dataset)} questions...")
    
    results = []
    latencies = []
    correct_count = 0
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, item in enumerate(dataset):
            question = item['question']
            expected = item['expected']  # 🔥 ИСПРАВЛЕНО: было 'expected_answer'
            
            # 2. Запрос к RAG API
            start_time = time.time()
            try:
                response = await client.post(
                    "http://localhost:8000/ask",
                    json={"question": question}
                )
                latency = time.time() - start_time
                latencies.append(latency)
                
                response_data = response.json()
                actual_answer = response_data.get('answer', '')
                
                # 3. LLM-as-a-Judge
                judge_prompt = JUDGE_TEMPLATE.format(
                    question=question,
                    expected_answer=expected,
                    actual_answer=actual_answer
                )
                
                # Дергаем Ollama напрямую для джуджи
                judge_response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "qwen2.5:7b",
                        "prompt": judge_prompt,
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0.1}
                    }
                )
                
                judge_raw = judge_response.json().get('response', '')
                
                # Парсим ответ джуджи
                json_match = re.search(r'\{.*\}', judge_raw, re.DOTALL)
                if json_match:
                    try:
                        judge_data = json.loads(json_match.group())
                        is_correct = judge_data.get('is_correct', False)
                    except json.JSONDecodeError:
                        is_correct = False
                else:
                    is_correct = False
                
                if is_correct:
                    correct_count += 1
                    
                results.append({
                    "question": question,
                    "expected": expected,
                    "actual": actual_answer,
                    "is_correct": is_correct,
                    "latency": latency
                })
                
                if (i + 1) % 5 == 0:
                    print(f"Processed {i + 1}/{len(dataset)}... Accuracy so far: {correct_count/(i+1)*100:.1f}%")
                    
            except Exception as e:
                print(f"❌ Error on question: {question}. Error: {e}")
                latencies.append(time.time() - start_time)

    # 4. Подсчет метрик
    accuracy = correct_count / len(dataset) if dataset else 0
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.5)] if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    
    print("\n" + "="*40)
    print("📊 EVALUATION RESULTS")
    print("="*40)
    print(f"Total Questions: {len(dataset)}")
    print(f"✅ Accuracy: {accuracy * 100:.2f}%")
    print(f"⏱️ Latency P50: {p50:.2f} sec")
    print(f"⏱️ Latency P95: {p95:.2f} sec")
    print("="*40)
    
    # 5. Сохраняем детальный отчет
    report_path = '/content/drive/MyDrive/faq-assistant-project/06-backups/stage_4_rag_data/evaluation_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "metrics": {"accuracy": accuracy, "p50": p50, "p95": p95},
            "details": results
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 Detailed report saved to: {report_path}")

asyncio.run(evaluate_dataset())
