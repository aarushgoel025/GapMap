import sys, json, glob
sys.path.insert(0, 'backend')

CONF_WEIGHTS = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
LEVEL_MULTIPLIER = 2.5
MAX_LEVEL = 10
MULTI_SOURCE_BONUS = 1.2
STUFFING_PENALTY = 0.5

for path in sorted(glob.glob('backend/data/profiles/candidate_*.json')):
    with open(path, encoding='utf-8') as f:
        profile = json.load(f)

    name = profile.get('full_name') or profile.get('name') or path
    dsa_skills = [s for s in profile.get('skills', []) if s.get('category_code') == 'DSA']
    if not dsa_skills:
        print(f"\n=== {name} === (0 DSA skills found, level = 0)")
        continue

    print(f"\n=== {name} ===")
    total_weight = 0.0
    estimated_level = 0

    for s in dsa_skills:
        sname = s.get('skill_name', '')
        conf = s.get('confidence', 'medium')
        w_base = CONF_WEIGHTS.get(conf, 0.0)

        vby = s.get('verified_by', [])
        bonus = MULTI_SOURCE_BONUS if len(vby) > 1 else 1.0

        is_stuffing = s.get('stuffing_flag', False)
        stuffing_mult = STUFFING_PENALTY if is_stuffing else 1.0

        w_final = w_base * bonus * stuffing_mult
        total_weight += w_final

        lvl_est = s.get('level_estimate')
        if conf == 'high' and isinstance(lvl_est, int):
            estimated_level = max(estimated_level, lvl_est)

        line = (f"  Skill: '{sname}' | confidence={conf} (w={w_base})"
                f" | verified_by={vby} (bonus={bonus})"
                f" | stuffing={is_stuffing} (mult={stuffing_mult})"
                f" | effective_weight={w_final:.2f}"
                f" | level_estimate={lvl_est}")
        print(line)

    calculated = min(MAX_LEVEL, round(LEVEL_MULTIPLIER * total_weight))
    final = max(calculated, estimated_level)

    print(f"  --- MATH ---")
    print(f"  total_weight = {total_weight:.2f}")
    print(f"  calculated   = min(10, round(2.5 × {total_weight:.2f})) = min(10, round({2.5*total_weight:.2f})) = {calculated}")
    print(f"  estimated_level (highest high-confidence LLM estimate) = {estimated_level}")
    print(f"  FINAL DSA LEVEL = max({calculated}, {estimated_level}) = {final}")

