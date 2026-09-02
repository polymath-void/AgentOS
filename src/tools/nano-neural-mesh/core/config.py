import logging

def get_logger():
    logger = logging.getLogger("NanoMesh-Cognitive")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - [C-CORE] - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger

class Settings:
    MESH_PORT = 8080
    MAX_NODES = 10000
    EPOCHS = 3
    PAYLOAD_PATH = "nodes/bin/neural_processor.wasm"
