# test_visibility_graph.py
import time
import sys
from pathlib import Path
# Ensure the repository root is on sys.path when this file is run directly.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.AStarPlanner import AStarPlanner
def main():
    env = MapEnvironment("path_algorithms/map1.json")
    startTime = time.time()
    # visibility_graph = env.generate_visibility_graph()
   
    aStar = AStarPlanner(env)
    plan = aStar.plan_path()
    print(f"Planning time: {time.time() - startTime:.4f} seconds")
    env.visualize_map(
        plan=plan,
        show_map=True,
        visibility_graph=aStar.graph,
    )
    


if __name__ == "__main__":
    main()