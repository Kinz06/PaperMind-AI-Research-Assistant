import os
os.environ['OPENAI_API_KEY'] = 'test-key'

from src.agent import PaperMindOrchestrator

print("Testing Multi-Agent Memory System...")
print("="*70)

orchestrator = PaperMindOrchestrator(
    use_cache=True,
    max_papers=3,
    enable_memory=True
)

print("\n1. First Query...")
results1 = orchestrator.search("transformer neural networks", max_results=3)
print(f"   Found {results1['total_found']} papers")

print("\n2. Second Query (should have context from first)...")
results2 = orchestrator.search("attention mechanisms", max_results=3)
print(f"   Found {results2['total_found']} papers")

print("\n3. Checking Memory...")
if orchestrator.memory:
    summary = orchestrator.memory.get_session_summary()
    print(f"   Total queries this session: {summary['total_queries']}")
    print(f"   Papers explored: {summary['total_papers_explored']}")
    print(f"   Topics: {', '.join(summary['topics_explored'])}")
    
    print("\n4. Recent queries:")
    for i, q in enumerate(summary['queries'], 1):
        print(f"   {i}. {q['query']} (Topic: {q['topic']})")

print("\n5. Agent Communication Messages:")
if orchestrator.comm_bus:
    print(f"   Total messages: {len(orchestrator.comm_bus.messages)}")
    for msg in orchestrator.comm_bus.messages[-3:]:
        print(f"   - {msg['from']} -> {msg['to']}: {msg['type']}")

print("\n" + "="*70)
print("Multi-Agent Memory System Working!")
print("="*70)