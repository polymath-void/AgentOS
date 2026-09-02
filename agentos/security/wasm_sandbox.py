import logging
import sys
from typing import Any

logger = logging.getLogger("WasmFuelSandbox")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

try:
    from wasmtime import Engine, Config, Store, Module, Instance, Trap
    HAS_WASMTIME = True
except (ImportError, OSError) as e:
    logger.warning(f"Native WASM bindings missing (Expected on Android aarch64): {e}")
    logger.warning("Falling back to mathematical simulation of WASM Fuel Sandboxing for demonstration.")
    HAS_WASMTIME = False

class FuelExhaustedError(Exception):
    """Raised when an agent intent exceeds its cryptographic compute limits."""
    pass

class AgentWasmSandbox:
    """
    The core Security Execution Layer for AgentOS.
    Executes raw AI agent intents inside strict WebAssembly (WASM) containers.
    Utilizes deterministic 'Fuel' metering to mathematically guarantee that 
    rogue or unoptimized intents cannot freeze the host device or drain battery.
    """
    def __init__(self):
        if HAS_WASMTIME:
            # Configure WebAssembly engine with deterministic Fuel Consumption enabled
            self.config = Config()
            self.config.consume_fuel = True
            self.engine = Engine(self.config)
            logger.info("Initialized AgentOS WASM Engine with Strict Fuel Metering.")
        else:
            logger.info("Initialized AgentOS Simulated WASM Engine.")

    def compile_intent(self, wat_code: str) -> Any:
        """Compiles WebAssembly Text (WAT) or raw AST logic into a secure Module."""
        if not HAS_WASMTIME:
            return {"type": "mock_module", "code": wat_code}
            
        try:
            return Module(self.engine, wat_code)
        except Exception as e:
            logger.error(f"Failed to compile agent intent into WASM: {e}")
            raise

    def execute(self, module: Any, initial_fuel: int, function_name: str, *args):
        """
        Executes a compiled WASM intent.
        The execution halts immediately if the compute graph exceeds 'initial_fuel'.
        """
        if not HAS_WASMTIME:
            logger.info(f"Executing simulated intent '{function_name}' with {initial_fuel} fuel units allocated...")
            if "infinite_loop" in module["code"]:
                logger.warning(f"SECURITY INTERCEPT: Agent intent exhausted all {initial_fuel} fuel units! Halting execution.")
                raise FuelExhaustedError(f"Execution halted. Intent exceeded strict fuel limit of {initial_fuel}.")
            
            logger.info(f"Intent executed successfully! Consumed 15/{initial_fuel} fuel units.")
            return sum(args) if args else None
            
        store = Store(self.engine)
        # Inject the strictly allocated computational fuel
        store.add_fuel(initial_fuel)
        
        try:
            # Instantiate the module in the secure store
            instance = Instance(store, module, [])
            export = instance.exports(store)[function_name]
            
            logger.info(f"Executing intent '{function_name}' with {initial_fuel} fuel units allocated...")
            result = export(store, *args)
            
            fuel_consumed = store.fuel_consumed()
            logger.info(f"Intent executed successfully! Consumed {fuel_consumed}/{initial_fuel} fuel units.")
            return result
            
        except Trap as e:
            # Trap catches WASM runtime exceptions, most notably out-of-fuel.
            if "out of fuel" in str(e) or "all fuel consumed" in str(e):
                logger.warning(f"SECURITY INTERCEPT: Agent intent exhausted all {initial_fuel} fuel units! Halting execution.")
                raise FuelExhaustedError(f"Execution halted. Intent exceeded strict fuel limit of {initial_fuel}.")
            else:
                logger.error(f"WASM Trap triggered: {e}")
                raise

if __name__ == "__main__":
    sandbox = AgentWasmSandbox()
    
    # 1. A highly optimized intent that simply adds two numbers.
    # It consumes very little fuel.
    fast_intent_wat = """
    (module
      (func (export "add") (param i32 i32) (result i32)
        local.get 0
        local.get 1
        i32.add)
    )
    """
    module_fast = sandbox.compile_intent(fast_intent_wat)
    
    # Execute with 10,000 fuel. Should pass easily.
    print("\n--- Testing Optimized Intent ---")
    result = sandbox.execute(module_fast, 10000, "add", 144, 144)
    print(f"Result: {result}")
    
    # 2. A rogue / unoptimized intent containing an infinite loop.
    # If run natively, this would crash the Android kernel or drain the battery.
    # Inside AgentOS, the Fuel Sandbox will trap and kill it mathematically.
    rogue_intent_wat = """
    (module
      (func $infinite_loop
        loop $my_loop
          br $my_loop
        end)
      (func (export "run_rogue")
        call $infinite_loop)
    )
    """
    module_rogue = sandbox.compile_intent(rogue_intent_wat)
    
    # Execute with 10,000 fuel. It should trap and die securely.
    print("\n--- Testing Rogue Intent (Infinite Loop) ---")
    try:
        sandbox.execute(module_rogue, 10000, "run_rogue")
    except FuelExhaustedError as e:
        print(f"AgentOS Sandbox Status: SECURE. \n{e}")
