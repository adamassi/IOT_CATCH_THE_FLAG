import heapq
import time
import numpy as np
from PARAMETERS import PlannerConfig



class AStarPlanner:
    def __init__(self, planning_env, timeout_seconds=None):
        self.start = tuple(planning_env.start)
        self.goal = tuple(planning_env.goal)
        self.planning_env = planning_env
        self.timeout_seconds = timeout_seconds
        self.start_time = time.time()

        # Build the visibility graph with timeout checks too.
        self.graph = self.generate_visibility_graph_with_timeout()

    def _timeout_reached(self):
        return (
            self.timeout_seconds is not None
            and time.time() - self.start_time >= self.timeout_seconds
        )

    def generate_visibility_graph_with_timeout(self):
        """
        Generate the visibility graph, but stop if the timeout is reached.
        This prevents A* from getting stuck before plan_path() even starts.
        """
        start = tuple(self.planning_env.start)
        goal = tuple(self.planning_env.goal)

        nodes = [start, goal] + [
            tuple(coord)
            for polygon in self.planning_env.obstacles[3:]
            for coord in polygon.exterior.coords[:-1]
        ]

        graph = {node: [] for node in nodes}

        for i, node1 in enumerate(nodes):
            if self._timeout_reached():
                print(f"A* visibility graph generation timed out after {self.timeout_seconds} seconds.")
                return graph

            for node2 in nodes[i + 1:]:
                if self._timeout_reached():
                    print(f"A* visibility graph generation timed out after {self.timeout_seconds} seconds.")
                    return graph

                if node1 != node2 and self.planning_env.is_visible(
                    np.array(node1),
                    np.array(node2)
                ):
                    distance = np.linalg.norm(np.array(node1) - np.array(node2))
                    graph[node1].append((node2, distance))
                    graph[node2].append((node1, distance))

        return graph

    def plan_path(self, timeout_seconds=None):
        # Use the given timeout, otherwise use the timeout from __init__.
        if timeout_seconds is not None:
            self.timeout_seconds = timeout_seconds
            self.start_time = time.time()

        open_set = []
        heapq.heappush(open_set, (0, self.start))
        came_from = {}
        g_score = {node: float('inf') for node in self.graph}
        g_score[self.start] = 0
        f_score = {node: float('inf') for node in self.graph}
        f_score[self.start] = np.linalg.norm(np.array(self.start) - np.array(self.goal))

        if not open_set:
            return np.array([])

        while open_set:
            # if self._timeout_reached():
            #     print(f"A* path planning timed out after {self.timeout_seconds} seconds.")
            #     return np.array([])

            _, current = heapq.heappop(open_set)

            if current == self.goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.start)
                return np.array(path[::-1])

            for neighbor, distance in self.graph[current]:
                if self._timeout_reached():
                    print(f"A* path planning timed out after {self.timeout_seconds} seconds.")
                    return np.array([])


                tentative_g_score = g_score[current] + distance
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + np.linalg.norm(
                        np.array(neighbor) - np.array(self.goal)
                    )
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        print("A* failed to find a path ")
        return np.array([])

    def plan(self, timeout_seconds=PlannerConfig.PATH_TIMEOUT_SECONDS):
        

        plan = self.plan_path(timeout_seconds=timeout_seconds)
        if plan is not None:
            self.planning_env.visualize_map(plan=plan, visibility_graph=self.graph, name='AStarPlan')
        return plan
