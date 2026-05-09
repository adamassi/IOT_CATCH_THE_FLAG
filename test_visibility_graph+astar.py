# test_visibility_graph.py

from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.AStarPlanner import AStarPlanner
def main():
    env = MapEnvironment("path_algorithms/map1.json")

    visibility_graph = env.generate_visibility_graph()
    aStar=AStarPlanner(env.start, env.goal, visibility_graph)
    env.visualize_map(
        # plan=aStar.plan_path(),
        show_map=True,
        visibility_graph=visibility_graph
    )


if __name__ == "__main__":
    main()