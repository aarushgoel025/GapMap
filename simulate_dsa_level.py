import sys, json
sys.path.insert(0, 'backend')

print('=== HOW DSA LEVEL IS COMPUTED: LIVE SIMULATION ===')
print()

CONF_W = {'high': 1.0, 'medium': 0.6, 'low': 0.3}

# ----- SCENARIO A -----
print('SCENARIO A: LLM extracted 1 DSA skill with level_estimate=7, confidence=high')
skills_a = [
    dict(skill_name='Data Structures', confidence='high', level_estimate=7, verified_by=[], stuffing_flag=False),
]
total_a = 0.0
est_a = 0
for s in skills_a:
    w = CONF_W[s['confidence']] * (1.2 if len(s['verified_by']) > 1 else 1.0) * (0.5 if s['stuffing_flag'] else 1.0)
    total_a += w
    if s['confidence'] == 'high' and isinstance(s['level_estimate'], int):
        est_a = max(est_a, s['level_estimate'])
calc_a = min(10, round(2.5 * total_a))
final_a = max(calc_a, est_a)
print(f'  weight=1.0, total_weight={total_a}')
print(f'  calculated = round(2.5 x {total_a}) = {round(2.5*total_a)} -> capped at 10 = {calc_a}')
print(f'  estimated_level (from LLM) = {est_a}')
print(f'  FINAL DSA LEVEL = max({calc_a}, {est_a}) = {final_a}')
print()

# ----- SCENARIO B -----
print('SCENARIO B: 3 DSA skills extracted, no level_estimate')
skills_b = [
    dict(skill_name='Data Structures', confidence='high', level_estimate=None, verified_by=[], stuffing_flag=False),
    dict(skill_name='Algorithms', confidence='high', level_estimate=None, verified_by=[], stuffing_flag=False),
    dict(skill_name='Dynamic Programming', confidence='medium', level_estimate=None, verified_by=[], stuffing_flag=False),
]
total_b = 0.0
est_b = 0
for s in skills_b:
    w = CONF_W[s['confidence']] * (1.2 if len(s['verified_by']) > 1 else 1.0) * (0.5 if s['stuffing_flag'] else 1.0)
    total_b += w
    print(f'  {s["skill_name"]}: conf={s["confidence"]}, w={w:.1f}')
calc_b = min(10, round(2.5 * total_b))
final_b = max(calc_b, est_b)
print(f'  total_weight = {total_b:.1f}')
print(f'  calculated = round(2.5 x {total_b:.1f}) = round({2.5*total_b:.1f}) = {calc_b}')
print(f'  FINAL DSA LEVEL = max({calc_b}, 0) = {final_b}')
print()

# ----- SCENARIO C -----
print('SCENARIO C: GitHub verification boosts the score (multi-source bonus)')
skills_c = [
    dict(skill_name='Data Structures', confidence='high', level_estimate=None, verified_by=['resume_claim', 'github'], stuffing_flag=False),
    dict(skill_name='Algorithms', confidence='medium', level_estimate=None, verified_by=[], stuffing_flag=False),
]
total_c = 0.0
for s in skills_c:
    base_w = CONF_W[s['confidence']]
    bonus = 1.2 if len(s['verified_by']) > 1 else 1.0
    w = base_w * bonus
    total_c += w
    print(f'  {s["skill_name"]}: base_w={base_w} x bonus={bonus} = {w:.2f} (verified_by={s["verified_by"]})')
calc_c = min(10, round(2.5 * total_c))
print(f'  total_weight = {total_c:.2f}')
print(f'  calculated = round(2.5 x {total_c:.2f}) = round({2.5*total_c:.2f}) = {calc_c}')
print(f'  FINAL DSA LEVEL = {calc_c}')
print()

# ----- SCENARIO D -----
print('SCENARIO D: Stuffing detected - penalty applies')
skills_d = [
    dict(skill_name='Data Structures', confidence='high', level_estimate=None, verified_by=[], stuffing_flag=False),
    dict(skill_name='Competitive Programming', confidence='high', level_estimate=None, verified_by=[], stuffing_flag=True),
]
total_d = 0.0
for s in skills_d:
    base_w = CONF_W[s['confidence']]
    stuffing = 0.5 if s['stuffing_flag'] else 1.0
    w = base_w * stuffing
    total_d += w
    print(f'  {s["skill_name"]}: base_w={base_w} x stuffing_mult={stuffing} = {w:.2f} (stuffing={s["stuffing_flag"]})')
calc_d = min(10, round(2.5 * total_d))
print(f'  total_weight = {total_d:.2f}')
print(f'  calculated = round(2.5 x {total_d:.2f}) = round({2.5*total_d:.2f}) = {calc_d}')
print(f'  FINAL DSA LEVEL = {calc_d}')

