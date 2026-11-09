# usage: ve_eval.sh AREA_DIR LABEL [view_edges args...]   -> one result line appended to ablation.tsv
PY="$USERPROFILE/.venvs/sidewalk-ai/Scripts/python.exe"; D=$1; LABEL=$2; shift 2
SFX="_$(echo $LABEL | tr -c 'A-Za-z0-9' '_')"
cd "/c/Users/nassi/OneDrive/Desktop/Sidewalks mapping/pipeline"
$PY view_edges.py --area-dir $D --out-suffix $SFX "$@" 2>&1 | grep -v Warn | tail -1 > /tmp/ve_$SFX.txt
$PY score.py --area-dir $D --gt-dir ../benchmark_dc/ground_truth --out ../benchmark_dc/ablation/$(basename $D)$SFX \
  --transects width_transects_views$SFX.geojson --widths width_samples_views$SFX.geojson 2>&1 | $PY -c "
import sys,json
t=sys.stdin.read(); s=json.loads(t[t.index('{'):]); w=s.get('width_same_station') or {}
line='\t'.join(map(str,['$(basename $D)','$LABEL',w.get('n'),w.get('mae_m'),w.get('bias_m'),w.get('median_abs_m'),w.get('within_0.5m_pct'),w.get('rmse_m')]))
print(line); open(r'C:/Users/nassi/OneDrive/Desktop/Sidewalks mapping/benchmark_dc/ablation/ablation.tsv','a').write(line+'\n')"
