"""Prompt Registry — управление версиями промптов."""

from app.prompts.base import (
    ZERO_SHOT_TEMPLATE,
    FEW_SHOT_TEMPLATE,
    COT_TEMPLATE,
    ROLE_TEMPLATE,
    CONSTRAINED_TEMPLATE,
    STRUCTURED_TEMPLATE,
    DECOMPOSITION_TEMPLATE,
)

PROMPT_REGISTRY = {
    "zero-shot": {
        "template": ZERO_SHOT_TEMPLATE,
        "version": "1.0",
        "description": "Базовый промпт без примеров",
        "author": "junior",
        "tags": ["baseline", "simple"],
    },
    "few-shot": {
        "template": FEW_SHOT_TEMPLATE,
        "version": "1.0",
        "description": "Промпт с 2 примерами",
        "author": "junior",
        "tags": ["examples", "standard"],
    },
    "cot": {
        "template": COT_TEMPLATE,
        "version": "1.0",
        "description": "Chain-of-Thought с пошаговым рассуждением",
        "author": "junior",
        "tags": ["reasoning", "complex"],
    },
    "role": {
        "template": ROLE_TEMPLATE,
        "version": "1.0",
        "description": "Role-based промпт с экспертной ролью",
        "author": "middle",
        "tags": ["role", "professional"],
    },
    "constrained": {
        "template": CONSTRAINED_TEMPLATE,
        "version": "1.0",
        "description": "Промпт с жёсткими ограничениями",
        "author": "middle",
        "tags": ["constraints", "short"],
    },
    "structured": {
        "template": STRUCTURED_TEMPLATE,
        "version": "1.0",
        "description": "Структурированный JSON-ответ",
        "author": "middle",
        "tags": ["json", "structured"],
    },
    "decomposition": {
        "template": DECOMPOSITION_TEMPLATE,
        "version": "1.0",
        "description": "Декомпозиция сложных вопросов",
        "author": "middle",
        "tags": ["complex", "decomposition"],
    },
}

FEATURE_FLAGS = {
    "production": ["zero-shot", "few-shot", "role"],
    "testing": ["cot", "constrained", "structured", "decomposition"],
}


def get_prompt(prompt_name: str) -> str:
    """Получить шаблон промпта по имени."""
    if prompt_name not in PROMPT_REGISTRY:
        raise ValueError(f"Промпт '{prompt_name}' не найден в реестре")
    return PROMPT_REGISTRY[prompt_name]["template"]


def list_prompts() -> list:
    """Список всех доступных промптов."""
    return list(PROMPT_REGISTRY.keys())


def get_prompt_info(prompt_name: str) -> dict:
    """Получить метаданные промпта."""
    if prompt_name not in PROMPT_REGISTRY:
        raise ValueError(f"Промпт '{prompt_name}' не найден в реестре")
    return {k: v for k, v in PROMPT_REGISTRY[prompt_name].items() if k != "template"}


def get_production_prompts() -> list:
    """Получить список промптов для продакшена."""
    return FEATURE_FLAGS["production"]


def get_testing_prompts() -> list:
    """Получить список промптов для тестирования."""
    return FEATURE_FLAGS["testing"]


if __name__ == "__main__":
    print("Доступные промпты:")
    for name in list_prompts():
        info = get_prompt_info(name)
        print(f"  - {name}: {info['description']} (v{info['version']}, {info['author']})")
    
    print(f"\nПродакшен: {get_production_prompts()}")
    print(f"Тестирование: {get_testing_prompts()}")
