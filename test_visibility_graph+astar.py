# test_visibility_graph.py
import time
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.AStarPlanner import AStarPlanner
def main():
    env = MapEnvironment("path_algorithms/map1.json")
    startTime = time.time()
    visibility_graph = env.generate_visibility_graph()
   
    aStar = AStarPlanner(env.start, env.goal, visibility_graph)
    plan = aStar.plan_path()
    print(f"Planning time: {time.time() - startTime:.4f} seconds")
    env.visualize_map(
        plan=plan,
        show_map=True,
        visibility_graph=visibility_graph
    )
    


if __name__ == "__main__":
    main()