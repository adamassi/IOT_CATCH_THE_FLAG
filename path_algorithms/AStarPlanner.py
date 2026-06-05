
import heapq
import numpy as np



class AStarPlanner:
    def __init__(self, planning_env):
        self.start = tuple(planning_env.start)
        self.goal = tuple(planning_env.goal)
        self.graph = planning_env.generate_visibility_graph()
        self.planning_env = planning_env

    def plan_path(self):
        # Implement A* path planning algorithm
        open_set = []
        heapq.heappush(open_set, (0, self.start))       
        came_from = {}
        g_score = {node: float('inf') for node in self.graph}
        g_score[self.start] = 0
        f_score = {node: float('inf') for node in self.graph}
        f_score[self.start] = np.linalg.norm(np.array(self.start) - np.array(self.goal))
        # Ensure the open_set is not empty and contains valid nodes
        if not open_set:
            return None
        while open_set:
            _, current = heapq.heappop(open_set)

            if current == self.goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.start)
                return np.array(path[::-1])

            for neighbor, distance in self.graph[current]:
                tentative_g_score = g_score[current] + distance
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + np.linalg.norm(np.array(neighbor) - np.array(self.goal))
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None
    def plan(self):
        # self.planning_env.visualize_map(name='beforePlantheAStar')
        plan = self.plan_path()
        
        # self.planning_env.visualize_map(plan=plan, visibility_graph=self.graph, name='AStarPlan')
        if plan is not None:
            self.planning_env.visualize_map(plan=plan, visibility_graph=self.graph, name='AStarPlan_BeforeSmoothing')
        return plan