use wasmtime::*;
use wasmtime_wasi::sync::WasiCtxBuilder;

pub fn execute_wasm(wasm_bytes: &[u8]) -> Result<(), anyhow::Error> {
    let engine = Engine::default();
    let mut linker = Linker::new(&engine);
    wasmtime_wasi::add_to_linker(&mut linker, |s| s)?;
    
    let wasi = WasiCtxBuilder::new()
        .inherit_stdio()
        .build();
        
    let mut store = Store::new(&engine, wasi);
    let module = Module::new(&engine, wasm_bytes)?;
    
    linker.module(&mut store, "", &module)?;
    let instance = linker.instantiate(&mut store, &module)?;
    let run = instance.get_typed_func::<(), (), _>(&mut store, "_start")?;
    
    run.call(&mut store, ())?;
    Ok(())
}
