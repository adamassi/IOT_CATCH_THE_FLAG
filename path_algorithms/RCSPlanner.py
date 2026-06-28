import heapq
import time
import numpy as np
from PARAMETERS import PlannerConfig


def _state_key(state):
    """Round to 6 decimal places to produce a stable dict/set key for float states."""
    return tuple(np.round(state, 6))


class Node:
    def __init__(self, state, resolution, rank, parent):
        self.state = state
        self.resolution = resolution
        self.rank = rank
        self.parent = parent

    def __lt__(self, other):
        # Primary: rank (cost). Secondary: lexicographic state (stable tie-break).
        if self.rank != other.rank:
            return self.rank < other.rank
        return tuple(self.state) < tuple(other.state)


class RCSPlanner(object):
    def __init__(self, planning_env):
        self.planning_env = planning_env
        self.expanded_nodes = []

        step_c = PlannerConfig.RCS_COARSE_STEP
        step_f = PlannerConfig.RCS_FINE_STEP
        self.coarseMoves = self._generate_moves(step_c)
        self.fineMoves = self._generate_moves(step_f)

    @staticmethod
    def _generate_moves(step):
        """Return 8-connected neighbour offsets (excluding (0,0)) for a given step size."""
        offsets = [-step, 0.0, step]
        moves = []
        for dx in reversed(offsets):
            for dy in reversed(offsets):
                if dx == 0.0 and dy == 0.0:
                    continue
                moves.append(np.array([dx, dy]))
        return moves

    def plan(self, timeout_seconds=PlannerConfig.PATH_TIMEOUT_SECONDS):
        """
        Compute and return the plan as a numpy array of shape (N, 2).
        Returns np.array([]) if no path is found or the timeout is reached.
        """
        start_time = time.time()
        env = self.planning_env
        self.expanded_nodes = []  # reset for each call

        rootNode = Node(env.start.copy(), 'coarse', 0, None)

        # closed list: set of rounded state tuples already expanded
        closedList = set()

        # Open list implemented as a min-heap with lazy deletion.
        # Each heap entry: (rank, counter, node)
        # best_rank[key] = lowest rank ever pushed for that state key.
        open_heap = []
        best_rank = {}
        _counter = [0]

        def push(node):
            key = _state_key(node.state)
            best_rank[key] = node.rank
            heapq.heappush(open_heap, (node.rank, _counter[0], node))
            _counter[0] += 1

        push(rootNode)

        plan = np.array([])

        while open_heap:
            if timeout_seconds is not None and time.time() - start_time >= timeout_seconds:
                print(f"[RCS] Planning timed out after {timeout_seconds} s.")
                return np.array([])

            rank, _, currentNode = heapq.heappop(open_heap)
            currentNode_state = currentNode.state
            key = _state_key(currentNode_state)

            # Lazy deletion: skip if a better path to this state was later found
            if best_rank.get(key) != rank:
                continue

            # Skip already-expanded nodes
            if key in closedList:
                continue
            closedList.add(key)
            self.expanded_nodes.append(currentNode_state)

            # Goal check: tolerance-based to handle floating-point coordinates
            if np.linalg.norm(currentNode_state - env.goal) <= PlannerConfig.RCS_GOAL_TOLERANCE:
                raw_path = self._reconstruct_path(currentNode)
                # Append the exact goal so the path terminates precisely at the target
                plan = np.vstack([raw_path, env.goal])
                break

            # Coarse expansion
            for action in self.coarseMoves:
                newNode_state = currentNode_state + action
                if (env.state_validity_checker(newNode_state) and
                        env.edge_validity_checker(currentNode_state, newNode_state)):
                    new_rank = currentNode.rank + 1
                    nkey = _state_key(newNode_state)
                    if best_rank.get(nkey, float('inf')) > new_rank:
                        push(Node(newNode_state, 'coarse', new_rank, currentNode))

            # Fine expansion from parent (transition to fine resolution)
            if currentNode.parent is not None and currentNode.resolution == 'coarse':
                parent = currentNode.parent
                parent_state = parent.state
                for action in self.fineMoves:
                    newNode_state = parent_state + action
                    if (env.state_validity_checker(newNode_state) and
                            env.edge_validity_checker(parent_state, newNode_state)):
                        new_rank = currentNode.rank + 1
                        nkey = _state_key(newNode_state)
                        if best_rank.get(nkey, float('inf')) > new_rank:
                            push(Node(newNode_state, 'fine', new_rank, parent))

        if len(plan) == 0:
            print("[RCS] Did not find any path to goal state.")
        else:
            path_len = sum(
                np.linalg.norm(plan[i + 1] - plan[i])
                for i in range(len(plan) - 1)
            )
            print(f"[RCS] Path found: {len(plan)} waypoints, total length {path_len:.3f} m, "
                  f"{len(self.expanded_nodes)} nodes expanded in "
                  f"{time.time() - start_time:.2f} s")

        return plan

    def _reconstruct_path(self, node):
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        path.reverse()
        return np.array(path)

    def get_expanded_nodes(self):
        """Return list of expanded node positions (no duplicates, in expansion order)."""
        return self.expanded_nodes
