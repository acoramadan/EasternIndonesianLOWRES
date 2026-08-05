from __future__ import annotations

import random
from typing import Any

def apply_split_strategy(
    records: list[dict[str, Any]],
    strategy: str,
    target_size: int = 1000,
    seed: int = 42,
) -> list[dict[str, Any]]:
    if strategy == "full":
        return records

    random.seed(seed)

    lang_groups: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        lang = r.get("source_lang", "unknown")
        lang_groups.setdefault(lang, []).append(r)

    if strategy == "test_2":
        sampled = []
        for group in lang_groups.values():
            sampled.extend(group[:2])
        return sampled

    if strategy == "lowest_verse_count":
        if not lang_groups:
            return records
        min_count = min(len(group) for group in lang_groups.values())
        sampled = []
        for group in lang_groups.values():
            sampled.extend(random.sample(group, min_count))
        random.shuffle(sampled)
        return sampled

    if strategy == "stratified":
        sampled = []
        pair_groups: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = {}
        for r in records:
            lang = r.get("source_lang", "unknown")
            direction = r.get("translation_direction", "unknown")
            text = r.get("source_text", "")
            words = len(text.split())
            if words < 10:
                length_cat = "short"
            elif words <= 25:
                length_cat = "medium"
            else:
                length_cat = "long"
            
            key = (lang, direction)
            pair_groups.setdefault(key, {}).setdefault(length_cat, []).append(r)
            
        for key, length_dict in pair_groups.items():
            total_in_pair = sum(len(lst) for lst in length_dict.values())
            pair_sampled = []
            
            for length_cat, lst in length_dict.items():
                if total_in_pair == 0:
                    continue
                cat_target = int((len(lst) / total_in_pair) * target_size)
                if cat_target >= len(lst):
                    pair_sampled.extend(lst)
                else:
                    pair_sampled.extend(random.sample(lst, cat_target))
            
            sampled.extend(pair_sampled)
            
        random.shuffle(sampled)
        return sampled

    return records
