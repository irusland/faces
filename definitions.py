import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.join(ROOT_DIR, "backend")
MODELS_DIR = os.path.join(ROOT_DIR, "models")
PHOTOS_SRC_DIR = os.path.join(ROOT_DIR, "src")
PHOTOS_RES_DIR = os.path.join(ROOT_DIR, "res")
PHOTOS_SRC_TEST_DIR = os.path.join(ROOT_DIR, "src_test")
PHOTOS_RES_TEST_DIR = os.path.join(ROOT_DIR, "res_test")
CACHE = os.path.join(CODE_DIR, "faces.pickle")
ENV_DIR = os.path.join(ROOT_DIR, "env")
TEST_ENV_PATH = os.path.join(ENV_DIR, "test.env")
DEV_ENV_PATH = os.path.join(ENV_DIR, "dev.env")
PROD_ENV_PATH = os.path.join(ENV_DIR, "prod.env")
TIMELINE_FILE = os.path.join(ROOT_DIR, "timeline.txt")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
TEST_LOGS_DIR = os.path.join(ROOT_DIR, "tests", "data", "test_logs")
PREDICTOR_PATH_68 = os.path.join(
    MODELS_DIR, "shape_predictor_68_face_landmarks.dat"
)
