# test_visibility_graph.py

from path_algorithms.MapEnvironment import MapEnvironment


def main():
    env = MapEnvironment("path_algorithms/map1.json")

    visibility_graph = env.generate_visibility_graph()

    env.visualize_map(
        show_map=True,
        visibility_graph=visibility_graph
    )


if __name__ == "__main__":
    main()