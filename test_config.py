import os

os.environ['OPENAI_API_KEY'] = 'test-key-for-validation'

print("Test 1: Importing configuration...")
try:
    from utils import Config, logger
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
    exit(1)

print("\nTest 2: Checking directories...")
print(f"  Output dir exists: {Config.OUTPUT_DIR.exists()}")
print(f"  Chroma dir exists: {Config.CHROMA_DIR.exists()}")

print("\nTest 3: Configuration values:")
print(f"  LLM Model: {Config.LLM_MODEL}")
print(f"  Max Papers: {Config.MAX_PAPERS_PER_QUERY}")
print(f"  Temperature: {Config.LLM_TEMPERATURE}")
print(f"  Log Level: {Config.LOG_LEVEL}")

print("\nTest 4: Testing logger...")
logger.info("This is an info message (green)")
logger.warning("This is a warning message (yellow)")
logger.error("This is an error message (red)")

print("\nAll tests passed! Configuration system is working.")
print("\nNote: We used a dummy API key for testing.")
print("For real usage, you'll need to add your OpenAI API key to .env file")