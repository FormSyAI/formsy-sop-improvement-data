#!/usr/bin/env python3
"""Stage-1 only SOP ablation host.

Arms:
  A baseline        : neutral system message only
  B neutral-long    : + length-matched generic design reference (no project rules)
  C sop-only        : + 8 FormSy SOP files from origin/main
  D sop+workbench   : same material as C, plus host-initiated workbench publish/show
                      executed AFTER the single model generation (receipt kept as
                      process evidence only; it cannot change the model input)

One stage, one inference, no retries, no overwrite.
"""
import argparse, asyncio, hashlib, json, os, re, subprocess, sys, time, traceback
from pathlib import Path

CONTEXT = 32768
OUTPUT = 4096
ENV = {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'HOME': os.environ['HOME'],
       'TMPDIR': os.environ.get('TMPDIR', '/tmp/'), 'LANG': 'en_US.UTF-8',
       'PYTHONDONTWRITEBYTECODE': '1'}

COMMON = ('你是软件设计助手。根据当前阶段用户输入，产出可供后续开发交接的完整设计，包括业务理解、'
          '规则与未知、状态及权限、数据与接口、实施任务和可验证验收场景，并做产品和技术自检。'
          '区分已给事实、待确认问题和建议；不要虚称用户确认、实施或测试。只输出当前阶段完整设计，不调用工具。')

NOTICE_SOP = ('本组由宿主提供下述 FormSy 0.5.4 文件原文作为设计参考。按相关要求使用材料，'
              '资料未覆盖的内容说明不确定。')
NOTICE_SOP_WB = ('本组由宿主提供下述 FormSy 0.5.4 文件原文作为设计参考；每阶段设计完成后由宿主发起'
                 '隔离工作台调用，这不是你自主调用，也不构成用户确认。按相关要求使用材料，'
                 '资料未覆盖的内容说明不确定。')
NOTICE_NEUTRAL = ('本组由宿主提供下述通用软件设计参考资料作为参考；资料不含本项目特定规则、'
                  '项目事实、评审结论或案例答案。按相关内容参考，资料未覆盖的内容说明不确定。')


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def put(p, text):
    p = Path(p)
    with p.open('x', encoding='utf-8') as f:
        f.write(text)


def put_json(p, obj):
    put(p, json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def render(role, content):
    return f'<|im_start|>{role}\n{content}<|im_end|>\n'


def strip_think(answer):
    s = answer.strip()
    if s.startswith('<think>'):
        if '</think>' not in s:
            raise RuntimeError('unclosed thinking block')
        return s.split('</think>', 1)[0] + '</think>', s.split('</think>', 1)[1].strip()
    if '<think>' in s or '</think>' in s:
        raise RuntimeError('malformed thinking block')
    return None, s


def token_count(tokenizer, model, text, folder):
    p = subprocess.run([str(tokenizer), '-m', str(model), '--stdin', '--ids', '--no-bos',
                        '--no-escape', '--offline'], input=text.encode(),
                       capture_output=True, timeout=900, env=ENV)
    (folder / 'tokenizer.stdout').write_bytes(p.stdout)
    (folder / 'tokenizer.stderr').write_bytes(p.stderr)
    if p.returncode:
        raise RuntimeError('tokenizer failure')
    import ast
    ids = ast.literal_eval(p.stdout.decode().strip())
    if not isinstance(ids, list) or not all(type(x) is int for x in ids):
        raise RuntimeError('invalid tokenizer output')
    return len(ids)


def infer(cli, tokenizer, model, prompt, seed, folder):
    prompt += '\n'
    put(folder / 'prompt.txt', prompt)
    count = token_count(tokenizer, model, prompt[:-1], folder)
    if count + 8 + OUTPUT > CONTEXT:
        raise RuntimeError(f'prompt {count} tokens exceeds frozen context')
    cmd = [str(cli), '-m', str(model), '-f', str(folder / 'prompt.txt'), '-no-cnv',
           '--no-display-prompt', '--no-escape', '--no-context-shift', '--offline',
           '--simple-io', '--perf', '-c', str(CONTEXT), '-n', str(OUTPUT), '-s', str(seed),
           '--temp', '0.6', '--top-p', '0.95', '--top-k', '20', '--min-p', '0',
           '-ngl', 'all', '-ctk', 'q8_0', '-ctv', 'q8_0', '-fa', 'on', '-t', '4']
    t0 = time.monotonic()
    rc = None
    timed_out = False
    with (folder / 'stdout.txt').open('xb') as so, (folder / 'stderr.txt').open('xb') as se:
        try:
            rc = subprocess.run(cmd, stdout=so, stderr=se, timeout=1800, env=ENV,
                                stdin=subprocess.DEVNULL).returncode
        except subprocess.TimeoutExpired:
            timed_out = True
    dur = round(time.monotonic() - t0, 3)
    err = (folder / 'stderr.txt').read_text(errors='replace')
    raw = (folder / 'stdout.txt').read_bytes()
    try:
        out = raw.decode('utf-8')
        invalid_utf8 = False
    except UnicodeDecodeError:
        out = raw.decode('utf-8', errors='replace')
        invalid_utf8 = True
    prompt_tok = re.search(r'prompt eval time\s*=.*?/\s*(\d+)\s*tokens', err)
    gen_tok = re.search(r'generate:.*?n_predict\s*=\s*(\d+)', err)
    eval_runs = re.findall(r'eval time\s*=.*?/\s*(\d+)\s*(?:runs|tokens)', err)
    meta = {'command': cmd, 'seed': seed, 'exit_code': rc, 'timeout': timed_out,
            'prompt_tokens': count, 'duration_seconds': dur,
            'prompt_eval_tokens_reported': int(prompt_tok.group(1)) if prompt_tok else None,
            'invalid_utf8_in_stdout': invalid_utf8,
            'max_predict': int(gen_tok.group(1)) if gen_tok else None,
            'eval_counts_reported': [int(x) for x in eval_runs]}
    put_json(folder / 'inference.json', meta)
    if timed_out:
        raise RuntimeError('inference timed out; partial output retained')
    marker = re.search(r' \[end of text\]\n(?:\n)*\Z', out)
    ctx = re.search(r'generate:\s*n_ctx\s*=\s*(\d+)', err)
    if rc or not marker:
        raise RuntimeError(f'incomplete generation or missing EOG (rc={rc})')
    if not prompt_tok or int(prompt_tok.group(1)) != count:
        raise RuntimeError('prompt token count mismatch between tokenizer and runtime')
    if not ctx or int(ctx.group(1)) < count + 8 + OUTPUT:
        raise RuntimeError('context window smaller than frozen requirement')
    if re.search(r'context.{0,20}(?:full|shift)|(?:truncate|truncation)|input too long', err, re.I):
        raise RuntimeError('possible truncation')
    answer = out[:marker.start()]
    if not answer.strip():
        raise RuntimeError('empty model answer')
    return answer, meta


async def publish_and_show(work, stage, sd, cli):
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
    current = work / f'stage{stage}-input.md'
    answer = work / f'stage{stage}-answer.md'
    event = {'conversation_id': 'ablation-offline', 'interaction_id': f'ablation-stage-{stage}',
             'reply_id': f'ablation-reply-{stage}', 'project_id': 'ablation-isolated',
             'project_title': '消融实验隔离项目', 'phase': 'product',
             'stage_status': 'in_progress', 'document_status': 'draft',
             'title': f'消融实验第 {stage} 阶段',
             'summary': '本阶段输入与模型产出已作为隔离草稿文件记录；仅为离线实验，不是用户确认。',
             'document_changes': [
                 {'path': p.name, 'revision': f'stage-{stage}', 'sha256': sha(p),
                  'summary': '离线重放的当前阶段输入' if p == current else '本地模型的当前阶段产出'}
                 for p in (current, answer)]}
    requests = [('publish', 'formsy_workbench_publish_update',
                 {'project_directory': str(work), 'event': event, 'presentation': 'update'}),
                ('show', 'formsy_workbench_show',
                 {'project_directory': str(work), 'view': 'overview'})]
    params = StdioServerParameters(command=str(cli), args=['workbench', 'serve', str(work),
                                                           '--workspace-root', str(work)], env=ENV)
    result = {}
    async with stdio_client(params) as (rd, wr):
        async with ClientSession(rd, wr) as session:
            init = await session.initialize()
            put_json(sd / 'mcp-initialize.json', json.loads(init.model_dump_json()))
            for label, name, arguments in requests:
                put_json(sd / f'host-{label}-request.json',
                         {'initiator': 'host', 'name': name, 'arguments': arguments})
                returned = await session.call_tool(name, arguments)
                data = json.loads(returned.model_dump_json())
                put_json(sd / f'host-{label}-response.json', data)
                if data.get('is_error'):
                    raise RuntimeError(f'workbench {label} returned is_error')
                result[label] = data
    pub = result['publish'].get('meta', {}).get('formsy/workbench', {})
    ev = pub.get('event', {})
    receipt = pub.get('receipt_sha256')
    if not receipt or ev.get('phase') != 'product' or ev.get('stage_status') != 'in_progress' \
            or ev.get('document_status') != 'draft':
        raise RuntimeError('unexpected publish receipt; raw retained')
    if ev.get('confirmation_verified') is not False:
        raise RuntimeError('receipt claims confirmation')
    shown = result['show'].get('meta', {}).get('formsy/workbench', {})
    if shown.get('interaction_sha256') != receipt:
        raise RuntimeError('show did not read back the published interaction')
    progress = shown.get('progress', {})
    summary = {'confirmation_state': progress.get('confirmation_state'),
               'initiator': 'host', 'stage': stage, 'phase': ev.get('phase'),
               'stage_status': ev.get('stage_status'),
               'document_status': ev.get('document_status'),
               'receipt_sha256': receipt,
               'meaning': '离线记录；非真实用户批准，非模型自主调用；在模型生成之后执行。'}
    put_json(sd / 'workbench-receipt-summary.json', summary)
    return summary


async def run(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cfg = json.loads(Path(args.config).read_text())
    arm = cfg['arm']
    sd = out / 'stage1'
    sd.mkdir()

    cli = args.bin_dir / 'llama-completion'
    tok = args.bin_dir / 'llama-tokenize'
    model = args.model

    # ---- material
    blocks = []
    used = []
    for path, digest in cfg['materials']:
        p = Path(path)
        actual = sha(p)
        if actual != digest:
            raise RuntimeError(f'material hash mismatch: {p}')
        text = p.read_text(encoding='utf-8')
        used.append({'path': str(p), 'sha256': digest, 'characters': len(text)})
        blocks.append(f'\n\n=== 来源: {p} | SHA-256: {digest} ===\n{text}\n=== 来源结束 ===')
    put_json(out / 'resources-used.json', used)

    stage = Path(cfg['stage_path'])
    if sha(stage) != cfg['stage_sha256']:
        raise RuntimeError('stage input hash mismatch')
    stage_text = stage.read_text(encoding='utf-8')
    put(sd / 'stage-input.md', stage_text)

    system = COMMON
    if arm in ('C', 'D'):
        system += '\n' + (NOTICE_SOP if arm == 'C' else NOTICE_SOP_WB) + ''.join(blocks)
    elif arm == 'B':
        system += '\n' + NOTICE_NEUTRAL + ''.join(blocks)

    manifest = {'arm': arm, 'arm_name': cfg['arm_name'], 'seed': cfg['seed'],
                'model_path': str(model), 'model_sha256': sha(model),
                'llama_sha256': sha(cli), 'tokenizer_sha256': sha(tok),
                'host_sha256': sha(Path(__file__)), 'config_sha256': sha(Path(args.config)),
                'stage_input': str(stage), 'stage_sha256': cfg['stage_sha256'],
                'material_chars': sum(x['characters'] for x in used),
                'material_files': len(used), 'context': CONTEXT,
                'max_generated_tokens_including_thinking': OUTPUT,
                'temperature': 0.6, 'top_p': 0.95, 'top_k': 20, 'min_p': 0,
                'gpu_layers': 'all', 'cache_type_k': 'q8_0', 'cache_type_v': 'q8_0',
                'flash_attention': 'on', 'threads': 4, 'inferences_per_run': 1,
                'workbench': 'host initiated after generation, receipt only' if arm == 'D' else 'not used'}
    put_json(out / 'manifest.json', manifest)

    work = out / 'workspace'
    work.mkdir()
    (work / 'stage1-input.md').write_text(stage_text, encoding='utf-8')

    prompt = render('system', system) + render('user', stage_text) + '<|im_start|>assistant\n'
    answer, meta = infer(cli, tok, model, prompt, cfg['seed'], sd)
    put(sd / 'model-answer.txt', answer)
    thought, final = strip_think(answer)
    if thought is None:
        raise RuntimeError('required thinking block missing')
    if not final.strip():
        raise RuntimeError('empty final answer')
    put(sd / 'thinking.txt', thought)
    put(sd / 'answer.md', final + '\n')
    (work / 'stage1-answer.md').write_text(final + '\n', encoding='utf-8')

    summary = {'arm': arm, 'seed': cfg['seed'], 'status': 'complete',
               'prompt_tokens': meta['prompt_tokens'],
               'duration_seconds': meta['duration_seconds'],
               'answer_chars': len(final), 'thinking_chars': len(thought),
               'answer_sha256': sha(sd / 'answer.md')}
    if arm == 'D':
        try:
            receipt = await publish_and_show(work, 1, sd, cfg['workbench_cli'])
            summary['workbench'] = {'status': 'ok', 'receipt_sha256': receipt['receipt_sha256'],
                                    'timing': 'after model generation'}
        except Exception as e:
            summary['workbench'] = {'status': 'failed', 'error': f'{type(e).__name__}: {e}'}
            put(sd / 'workbench-failure.txt', traceback.format_exc())
    put_json(out / 'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--model', required=True, type=Path)
    ap.add_argument('--bin-dir', required=True, type=Path)
    args = ap.parse_args()
    try:
        return asyncio.run(run(args))
    except Exception:
        try:
            (args.output / 'fatal.txt').write_text(traceback.format_exc(), encoding='utf-8')
        except Exception:
            pass
        raise


if __name__ == '__main__':
    sys.exit(main())
