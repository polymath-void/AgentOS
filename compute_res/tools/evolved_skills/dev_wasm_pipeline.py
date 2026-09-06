"""\nSkill: dev_wasm_pipeline\nCategory: developer-tools\nDescription: Safe redesign of WASM-Bridge: Generates compilation commands for safely building C/Rust to WASM.\n"""\n\ndef run(**kwargs):
    import os
    source_file = kwargs.get('source_file', '')
    output_wasm = kwargs.get('output_wasm', 'out.wasm')
    if not source_file or not os.path.exists(source_file): return {'error': 'source_file not found'}
    cmd = ['emcc', source_file, '-O3', '-s', 'WASM=1', '-o', output_wasm]
    return {'command_to_run': ' '.join(cmd), 'status': 'ready_to_build', 'note': 'Execute this command to safely compile to WASM.'}
