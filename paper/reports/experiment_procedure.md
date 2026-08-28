# 正式实验详细操作流程

> 版本: v1.0 | 日期: 2026-07-26
> 实验类型: 定量对比实验
> 预计工期: 6-8周

---

## 第一章：实验环境搭建

### 1.1 硬件要求

- CPU: 64-bit x86, 4核以上
- 内存: 8GB 以上
- 磁盘: 20GB 可用空间
- 操作系统: Ubuntu 20.04 或 22.04 LTS

### 1.2 安装虚拟机（如无 Linux 物理机）

```
# Windows 宿主: 安装 VirtualBox 或 VMware Workstation
# 下载 Ubuntu 22.04 LTS ISO
# 创建虚拟机: 4核, 8GB RAM, 30GB 磁盘
# 安装 Ubuntu, 完成后更新系统

sudo apt update && sudo apt upgrade -y
```

### 1.3 安装 OCaml 编译环境

```
# 安装 OCaml 包管理器
sudo apt install -y opam

# 初始化 OPAM
opam init -y
eval $(opam env)

# 安装 OCaml 编译器 (4.14.x 版本，论文工具的兼容版本)
opam switch create 4.14.1
eval $(opam env)
```

### 1.4 安装 APRON 数值抽象域库

```
# 安装系统依赖
sudo apt install -y libgmp-dev libmpfr-dev libppl-dev

# 通过 OPAM 安装 APRON
opam install -y apron

# 验证安装
ocamlfind query apron
```

### 1.5 安装 BDDAPRON 库

```
# BDDAPRON 依赖 APRON，从 OPAM 安装
opam install -y bddapron

# 验证安装
ocamlfind query bddapron
```

### 1.6 安装 Z3 SMT 求解器

```
# 安装 Z3
sudo apt install -y z3

# 安装 Z3 OCaml 绑定
opam install -y z3

# 验证
z3 --version
```

### 1.7 下载并编译 Dimovski 工具

```
# 下载 Zenodo artifact
cd ~
wget "https://zenodo.org/api/records/8167960/files/ErrorInvariants.tar.gz/content" \
     -O ErrorInvariants.tar.gz

# 解压
tar -xzf ErrorInvariants.tar.gz
cd ErrorInvariants/

# 阅读安装说明
cat HowToInstall.txt

# 编译（具体命令以 HowToInstall.txt 为准，通常为）
make

# 验证编译成功
./faultloc --help   # 或查看可执行文件是否存在
```

### 1.8 准备实验目录

```
mkdir -p ~/experiment
cd ~/experiment
mkdir -p {programs,results,dumps,logs,scripts}
```

### 1.9 安装 Python 分析环境 （用于 LLM 调用和格式化）

```
sudo apt install -y python3 python3-pip
pip3 install openai anthropic matplotlib scipy pandas
```

---

## 第二章：实验程序选取

### 2.1 选取来源

SV-COMP 2024 基准集，聚焦以下子类别：

| 子类别 | 说明 | 候选数量 |
|--------|------|---------|
| loop-simple | 简单循环 | 8 |
| loop-new | 基础循环模式 | 11 |
| loop-lit | 文献中的经典循环程序 | 33 |
| loops-crafted-1 | 手工构造的循环验证任务 | 55 |
| ntdrivers | Windows 驱动简化版（控制流） | 12 |

总计候选: ~119 个程序

### 2.2 筛选标准

**包含条件**：
- 纯整数变量运算（无数组、无指针、无浮点）
- C 语言
- 代码行数 ≤ 50 行
- 含明确的断言点 (`assert`, `__VERIFIER_assert`, 或 `reach_error`)

**排除条件**：
- 含 `a[i]` 数组访问
- 含 `*p` 指针解引用
- 含 `float`/`double` 类型
- 含 `struct`/`union` 类型
- 含递归函数调用
- 含 `malloc`/`free` 堆操作

### 2.3 选定的实验程序集（15个）

| 编号 | 来源目录 | 文件名 | 行数 | 类型 | 特征 |
|------|---------|--------|------|------|------|
| S01 | Dimovski论文 | program1 | 4 | BUGGY | 纯线性链，无分支 |
| S02 | Dimovski论文 | program2 | 6 | BUGGY | if-else 条件分支 |
| S03 | Dimovski论文 | program3 | 8 | BUGGY | while 循环，常数边界 |
| S04 | loop-simple | nested_1.c | 12 | SAFE | for 循环，简单嵌套 |
| S05 | loop-new | count_by_k.c | 11 | SAFE | for 循环，步长为 k |
| S06 | loop-new | half.c | 14 | BUGGY | for 循环，if-else 在内 |
| S07 | loop-new | gauss_sum.c | 13 | SAFE | for 循环，高斯求和 |
| S08 | loop-lit | afnp2014.c | 16 | SAFE | while 循环，变量间依赖 |
| S09 | loop-lit | cggmp2005.c | 17 | BUGGY | while 循环，条件依赖 |
| S10 | loop-lit | gj2007.c | 19 | BUGGY | for 循环，复杂条件 |
| S11 | loops-crafted-1 | Mono5_1.c | 16 | BUGGY | while + 内嵌 if |
| S12 | loops-crafted-1 | mono-crafted_12.c | 17 | SAFE | while + 内嵌 if，模运算 |
| S13 | ntdrivers | kbfiltr.i.cil-1.c | ~20 | BUGGY | 控制流密集 |
| S14 | loops | (手动挑选) | ~15 | BUGGY | 多循环嵌套 |
| S15 | 自编 | buggy_loop_if | 10 | BUGGY | 循环内嵌 if-else |

类型分布: 8 BUGGY, 5 SAFE, 2 边界情况

### 2.4 对每个程序标注 Ground Truth

对每个 BUGGY 程序，人工标注：
- `bug_line`: 真正 bug 所在的行号
- `relevant_lines`: Dimovski 应该判定为相关的行号列表
- `irrelevant_lines`: Dimovski 应该判定为无关的行号列表

对每个 SAFE 程序，标注：
- `expected_result`: SAFE（Dimovski 应返回 ⊥）

### 2.5 将选定程序复制到实验目录

```
cd ~/experiment/programs

# S01-S03: 手工输入 Dimovski 论文程序
cat > s01_program1.c << 'EOF'
int main() {
    int n, z, y;
    z = n + 1;
    y = z;
    z = z + 1;
    assert(y < n);
    return 0;
}
EOF

# ... (每个程序类似)

# S04-S13: 从 SV-COMP 克隆目录复制
cp ~/sv-benchmarks/c/loop-simple/nested_1.c ~/experiment/programs/s04_nested_1.c
cp ~/sv-benchmarks/c/loop-new/count_by_k.c ~/experiment/programs/s05_count_by_k.c
# ... (类推)

# 检查所有程序是否就位
ls -la ~/experiment/programs/s*.c | wc -l   # 应输出 15
```

---

## 第三章：修改 Dimovski 工具以导出中间数据

### 3.1 定位关键代码

在 Dimovski 源码中找到 `faultLoc.ml`（或类似名称的主模块文件），找到 `FaultLoc` 函数中调用 `AbsAnalysis` 的位置和最终调用 `Slice` 的位置。

### 3.2 插入导出代码

在最终一次 `AbsAnalysis` 完成后、`Slice` 调用之前，插入以下 OCaml 代码：

```ocaml
(* === 插入: 导出 Error Invariant 序列 === *)
let export_errinv filename errinv_map =
  let oc = open_out filename in
  LabelMap.iter (fun label inv ->
    Printf.fprintf oc "LOC: %s\n" (Label.to_string label);
    Printf.fprintf oc "INV: %s\n" (A.to_string inv);
    Printf.fprintf oc "---\n"
  ) errinv_map;
  close_out oc
in

(* 在迭代收敛后、Slice 前调用 *)
let dump_file = "~/experiment/dumps/" ^ prog_name ^ "_errinv.txt" in
export_errinv dump_file errinv_map;

(* 同时导出谓词集 *)
let pred_file = "~/experiment/dumps/" ^ prog_name ^ "_predicates.txt" in
let oc = open_out pred_file in
List.iter (fun p -> Printf.fprintf oc "%s\n" (Predicate.to_string p)) pred_set;
close_out oc;

(* 导出切片结果 *)
let slice_file = "~/experiment/dumps/" ^ prog_name ^ "_slice.txt" in
let oc = open_out slice_file in
Printf.fprintf oc "RELEVANT: %s\n" (String.concat "," (List.map Label.to_string relevant_labels));
Printf.fprintf oc "IRRELEVANT: %s\n" (String.concat "," (List.map Label.to_string irrelevant_labels));
close_out oc;

(* === 插入结束 === *)
```

### 3.3 导出运行时间

在主函数中添加计时：

```ocaml
let start_time = Unix.gettimeofday () in
(* ... FaultLoc 调用 ... *)
let end_time = Unix.gettimeofday () in
let elapsed = end_time -. start_time in
Printf.printf "TIME: %.4f seconds\n" elapsed;
Printf.printf "ITERATIONS: %d\n" num_iterations;
```

### 3.4 重新编译

```bash
cd ~/ErrorInvariants/
make clean
make
# 确认生成的可执行文件中包含导出功能
```

---

## 第四章：批量运行实验

### 4.1 编写批量运行脚本

```bash
#!/bin/bash
# ~/experiment/scripts/run_all.sh

PROGRAMS_DIR="$HOME/experiment/programs"
RESULTS_DIR="$HOME/experiment/results"
DUMPS_DIR="$HOME/experiment/dumps"
LOGS_DIR="$HOME/experiment/logs"
FAULTLOC="$HOME/ErrorInvariants/faultloc"

mkdir -p "$RESULTS_DIR" "$DUMPS_DIR" "$LOGS_DIR"

for prog in "$PROGRAMS_DIR"/s*.c; do
    prog_name=$(basename "$prog" .c)
    echo "[$(date)] Running: $prog_name"
    
    # 运行 Dimovski，超时 300 秒
    timeout 300 "$FAULTLOC" "$prog" \
        > "$RESULTS_DIR/${prog_name}_output.txt" \
        2> "$LOGS_DIR/${prog_name}_stderr.log"
    
    exit_code=$?
    
    # 记录结果摘要
    if [ $exit_code -eq 0 ]; then
        echo "$prog_name: OK" >> "$RESULTS_DIR/summary.txt"
    elif [ $exit_code -eq 124 ]; then
        echo "$prog_name: TIMEOUT" >> "$RESULTS_DIR/summary.txt"
    else
        echo "$prog_name: ERROR (exit=$exit_code)" >> "$RESULTS_DIR/summary.txt"
    fi
    
    # 移动 dump 文件到 dumps 目录
    mv "$DUMPS_DIR"/*_errinv.txt "$DUMPS_DIR/${prog_name}_errinv.txt" 2>/dev/null
    mv "$DUMPS_DIR"/*_predicates.txt "$DUMPS_DIR/${prog_name}_predicates.txt" 2>/dev/null
    mv "$DUMPS_DIR"/*_slice.txt "$DUMPS_DIR/${prog_name}_slice.txt" 2>/dev/null
done

echo "[$(date)] ALL DONE"
```

### 4.2 执行批量运行

```bash
chmod +x ~/experiment/scripts/run_all.sh
bash ~/experiment/scripts/run_all.sh 2>&1 | tee ~/experiment/logs/full_run.log
```

### 4.3 预期产出

每个程序 4 个输出文件：

| 文件 | 内容 | 示例 |
|------|------|------|
| `sXX_output.txt` | FaultLoc 标准输出 + TIME + ITERATIONS | `RELEVANT: 1,2,4` |
| `sXX_errinv.txt` | 每个位置的 Error Invariant 约束 | `LOC: ① INV: [y=n+1]` |
| `sXX_predicates.txt` | BDD 精化用谓词集 | `y<0` |
| `sXX_slice.txt` | 相关/无关标签列表 | `RELEVANT: 1,2,4` |

---

## 第五章：格式化管道

### 5.1 步骤概览

```
Dump 文件 → Python 解析 → 矩阵转表达式 → 相邻比较 → 标注变化 → JSON 输出
```

### 5.2 解析 Dump 文件

```python
# ~/experiment/scripts/parse_dump.py

import re, json, os

def parse_errinv(filepath):
    """解析 Dimovski dump 文件，返回每位置的约束列表"""
    with open(filepath) as f:
        content = f.read()
    
    locations = {}
    blocks = content.strip().split('---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        loc_match = re.search(r'LOC:\s*(\S+)', block)
        inv_match = re.search(r'INV:\s*\[(.+?)\]', block, re.DOTALL)
        if loc_match and inv_match:
            loc = loc_match.group(1)
            inv_text = inv_match.group(1).strip()
            # 解析约束: "y=n+1, x≥5" → ["y=n+1", "x≥5"]
            constraints = [c.strip() for c in inv_text.split(',') if c.strip()]
            locations[loc] = constraints
    return locations

def parse_predicates(filepath):
    """解析谓词集"""
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]

def parse_slice(filepath):
    """解析切片结果"""
    with open(filepath) as f:
        content = f.read()
    relevant = re.search(r'RELEVANT:\s*(.+)', content)
    irrelevant = re.search(r'IRRELEVANT:\s*(.+)', content)
    return {
        'relevant': relevant.group(1).split(',') if relevant else [],
        'irrelevant': irrelevant.group(1).split(',') if irrelevant else []
    }
```

### 5.3 标注变化类型

```python
def classify_change(prev_inv, curr_inv):
    """比较相邻位置 invariant，返回变化类型"""
    if prev_inv == curr_inv:
        return "SAME"
    
    prev_vars = extract_variables(prev_inv)
    curr_vars = extract_variables(curr_inv)
    
    entering = curr_vars - prev_vars
    exiting = prev_vars - curr_vars
    
    if not prev_inv or prev_inv == ['⊤']:
        return "ENTER"
    if not curr_inv or curr_inv == ['⊥']:
        return "CONTRADICT"
    if exiting and not entering:
        return "EXIT"
    if entering:
        return "TRANSFER" if exiting else "ENTER"
    return "REFINE"
```

### 5.4 产出标准 JSON

```python
def format_trajectory(prog_name, source_code, errinv, predicates, slice_result):
    """组装最终 JSON"""
    trajectory = []
    sorted_locs = sorted(errinv.keys())
    
    for i, loc in enumerate(sorted_locs):
        prev_inv = errinv[sorted_locs[i-1]] if i > 0 else []
        curr_inv = errinv[loc]
        change = classify_change(prev_inv, curr_inv)
        
        trajectory.append({
            "loc": loc,
            "line": get_line_number(source_code, loc),
            "code": get_code(source_code, loc),
            "invariant": format_invariant(curr_inv),
            "change": change,
            "entering_vars": list(get_entering(prev_inv, curr_inv)),
            "exiting_vars": list(get_exiting(prev_inv, curr_inv))
        })
    
    return {
        "program": prog_name,
        "source": source_code,
        "assertion_point": sorted_locs[-1],
        "predicates": predicates,
        "iterations": get_iteration_count(prog_name),
        "slice_dimovski": slice_result,
        "trajectory": trajectory
    }
```

### 5.5 运行格式化管道

```bash
cd ~/experiment
python3 scripts/format_all.py \
    --dumps dumps/ \
    --programs programs/ \
    --results results/ \
    --output formatted/
```

---

## 第六章：LLM 评估实验

### 6.1 实验设计

| 条件 | 输入 | 说明 |
|------|------|------|
| **Ours (Invariant)** | 格式化 invariant 轨迹 JSON | 本方法 |
| **Code Only** | 仅源代码 + 错误位置 | LLM 直接读代码 |
| **Dimovski Native** | Dimovski 原生切片（行号列表） | 无需 LLM，直接对比 |
| **Ochiai (SBFL)** | SBFL 可疑度排名 | 经典 baseline |
| **Cause Transitions** | 状态差异点 | 动态 baseline |

### 6.2 LLM Prompt 模板

**Ours (Invariant) Prompt**:

```
你是一个程序分析解释器。以下是由抽象解释产生的Error Invariant轨迹。

Error Invariant是每个程序位置上"可能导致断言失败的状态"的数学描述。
相邻位置invariant相同 → 中间语句与错误无关，可安全删除。
相邻位置invariant不同 → 中间语句参与了错误传播。

请完成以下任务：
1. 逐位置解释: invariant表达了什么？为什么变化/不变？
2. 判断每条语句是否与错误相关
3. 如果相关，它在错误传播链中的角色是什么？
4. 对无关语句，解释为什么无关

[粘贴格式化的 invariant 轨迹 JSON]

输出格式（严格JSON）:
{
  "analysis": [
    {"loc": "①", "relevant": true/false, "role": "SOURCE|PROPAGATION|SINK|NONE",
     "explanation": "..."}
  ],
  "bug_summary": "一句话描述bug原因",
  "suggested_fix": "修复建议"
}
```

**Code Only Prompt**（对照）:

```
以下是一个包含bug的C程序。断言在最后一行失败。
请分析程序，判断每条语句是否与错误相关。

[粘贴源代码]

输出格式（严格JSON，同上）
```

### 6.3 LLM 调用脚本

```python
# ~/experiment/scripts/eval_llm.py

import json, time
from openai import OpenAI

client = OpenAI()

def query_llm(prompt, model="gpt-4o"):
    """调用 LLM，返回结构化输出"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个程序分析专家。严格按照要求的JSON格式输出。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,  # 确保可复现
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def evaluate_single(prog_name, trajectory_json, source_code, ground_truth):
    """对单个程序跑所有条件"""
    results = {}
    
    # 条件1: Ours (Invariant)
    prompt_inv = build_invariant_prompt(trajectory_json)
    start = time.time()
    result_inv = query_llm(prompt_inv)
    results['ours'] = {
        'output': result_inv,
        'time': time.time() - start,
        'accuracy': compare_to_ground_truth(result_inv, ground_truth)
    }
    
    # 条件2: Code Only
    prompt_code = build_code_prompt(source_code)
    start = time.time()
    result_code = query_llm(prompt_code)
    results['code_only'] = {
        'output': result_code,
        'time': time.time() - start,
        'accuracy': compare_to_ground_truth(result_code, ground_truth)
    }
    
    return results

# 批量运行
all_results = {}
for prog in programs:
    print(f"Evaluating: {prog['name']}")
    trajectory = load_trajectory(prog['name'])
    source = load_source(prog['name'])
    gt = load_ground_truth(prog['name'])
    all_results[prog['name']] = evaluate_single(
        prog['name'], trajectory, source, gt
    )
    time.sleep(1)  # API 限速

# 保存结果
with open('results/llm_eval_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
```

### 6.4 评估指标

对每个程序，对比 LLM 输出与人工 ground truth：

```python
def compare_to_ground_truth(llm_output, ground_truth):
    """计算精确率、召回率、F1"""
    llm_relevant = set()
    for entry in llm_output['analysis']:
        if entry['relevant']:
            llm_relevant.add(entry['loc'])
    
    gt_relevant = set(ground_truth['relevant_lines'])
    
    tp = len(llm_relevant & gt_relevant)
    fp = len(llm_relevant - gt_relevant)
    fn = len(gt_relevant - llm_relevant)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp, 'fp': fp, 'fn': fn,
        'slice_size': len(llm_relevant),
        'gt_size': len(gt_relevant)
    }
```

### 6.5 统计检验

```python
from scipy import stats

# 对 Ours vs Code Only 做配对 t 检验
ours_f1 = [r['ours']['accuracy']['f1'] for r in all_results.values()]
code_f1 = [r['code_only']['accuracy']['f1'] for r in all_results.values()]

t_stat, p_value = stats.ttest_rel(ours_f1, code_f1)
print(f"Paired t-test: t={t_stat:.3f}, p={p_value:.4f}")

# 效应量 (Cohen's d)
diff = [o - c for o, c in zip(ours_f1, code_f1)]
cohens_d = np.mean(diff) / np.std(diff, ddof=1)
print(f"Cohen's d: {cohens_d:.3f}")
```

---

## 第七章：人工审查

### 7.1 LLM 输出的语义质量审查

对每个程序，3 名评审者独立审查 LLM 的 invariant 解释：

**评分维度**（各 1-5 分）：
- **忠实度**: LLM 的描述是否忠实于 invariant 的数学含义？
- **有用性**: 该描述是否有助于理解错误传播？
- **可验证性**: 描述中的断言能否追溯到具体 invariant 证据？

**评分表**：

```python
review_scores = {
    "reviewer_id": "...",
    "prog_name": "S01",
    "ours": {
        "faithfulness": 4,
        "usefulness": 5, 
        "verifiability": 4,
        "notes": "..."
    },
    "code_only": {
        "faithfulness": 3,
        "usefulness": 3,
        "verifiability": 2,
        "notes": "..."
    }
}
```

### 7.2 评分者间一致性

```python
from sklearn.metrics import cohen_kappa_score

# 计算三位评审者在忠实度评分上的 Cohen's κ
kappa_ours = cohen_kappa_score(r1['ours']['faithfulness'], r2['ours']['faithfulness'])
print(f"Inter-rater agreement (Ours, faithfulness): κ={kappa_ours:.3f}")
```

---

## 第八章：汇总与报告

### 8.1 生成汇总表

对每个程序、每个条件汇总：

| 程序 | 条件 | Precision | Recall | F1 | Slice Size | LLM Time(s) | 忠实度评分 |
|------|------|-----------|--------|-----|-----------|-------------|-----------|
| S01 | Ours | | | | | | |
| S01 | Code Only | | | | | | |
| S02 | Ours | | | | | | |
| ... | ... | | | | | | |

### 8.2 切片大小对比

对比 Dimovski 原生切片 vs LLM-invariant 切片 vs SBFL Top-N：

| 程序 | Dimovski 原生 | LLM-Invariant | LLM-Code Only | Ochiai | 缩减率 (Ours vs Dim) |
|------|-------------|--------------|--------------|--------|---------------------|
| S01 | 4 | 3 | 3 | 5 | 25% |
| ... | | | | | |

### 8.3 生成图表

```python
import matplotlib.pyplot as plt

# F1 对比柱状图
fig, ax = plt.subplots()
conditions = ['Ours', 'Code Only', 'Dimovski Native', 'Ochiai']
f1_means = [np.mean([...]), ...]
ax.bar(conditions, f1_means)
ax.set_ylabel('F1 Score')
ax.set_title('Fault Localization Accuracy Comparison')
plt.savefig('results/f1_comparison.png')
```

---

## 第九章：实验检查清单

- [ ] Linux VM 安装完成
- [ ] OCaml 4.14.1 编译环境就绪
- [ ] APRON + BDDAPRON 库安装并验证
- [ ] Z3 安装并可从命令行调用
- [ ] Dimovski artifact 编译成功，自带测试通过
- [ ] 导出代码插入并重新编译
- [ ] 15 个程序复制到实验目录
- [ ] Ground truth 人工标注完成
- [ ] 批量运行脚本通过单程序测试
- [ ] 所有 15 个程序成功运行（无超时/崩溃）
- [ ] Dump 文件格式验证正确
- [ ] Python 格式化管道在 3 个程序上验证
- [ ] LLM API Key 配置并验证连接
- [ ] 所有 15 个程序 × 2 条件 = 30 次 LLM 调用完成
- [ ] 人工审查评分收集完毕
- [ ] 统计检验完成
- [ ] 图表生成
- [ ] 实验报告初稿
