# This code was partly written by Oren Salzman and Dean Zadok, and partly by Yotam Granov

import numpy as np
from path_algorithms.RRTTree import RRTTree
import time

class RRTStarPlanner(object):
    def __init__(self, planning_env, ext_mode, goal_prob, k):
        # Initialize the planning environment and the RRT* tree
        self.planning_env = planning_env
        self.tree = RRTTree(self.planning_env)

        # Set search parameters
        self.ext_mode = ext_mode  # Extension mode (e.g., E1 or E2)
        self.goal_prob = goal_prob  # Probability of sampling the goal
        self.k = k  # Number of nearest neighbors for rewiring

        # Set step size for extensions based on the environment size
        if planning_env.ylimit[1] < 100:
            self.step_size = 0.2  # Small step size for small environments
        else:
            self.step_size = 10

    def plan(self):
        '''
        Compute and return the plan. The function should return a numpy array containing the states (positions) of the robot.
        '''
        start_time = time.time()  # Start timing the planning process
        
        env = self.planning_env
        self.tree.add_vertex(env.start)  # Add the start state to the tree

        log = False
        if self.k == 0:  # Enable log mode if k is 0
            log = True

        goal_added = False  # Flag to indicate if the goal has been added to the tree
        num_iter = 0  # Counter for the number of iterations
        num_rewires = 0  # Counter for the number of rewiring operations
        plan = []  # List to store the final plan

        # Main loop: Continue until the goal is added to the tree
        while not goal_added:
            num_iter += 1
            goal = False  # Flag to indicate if the current sample is the goal

            # Add goal biasing: Sample the goal with a probability of `goal_prob`
            p = np.random.uniform()
            if p < self.goal_prob:
                s = env.goal  # Sample the goal
                goal = True
            else:
                # Sample a random state within the environment bounds
                x = np.random.uniform(env.xlimit[0], env.xlimit[1])
                y = np.random.uniform(env.ylimit[0], env.ylimit[1])
                s = [x, y]

            # Check if the sampled state is valid (in free space)
            if env.state_validity_checker(s):
                nearest_vert = self.tree.get_nearest_state(s)  # Find the nearest vertex in the tree
                nearest_vert_idx = nearest_vert[0]  # Get the index of the nearest vertex

                # Perform partial extensions if extension mode is E2
                if self.ext_mode == 'E2':
                    s, goal_added = self.extend(nearest_vert[1], s)  # Extend towards the sampled state
                    if not env.state_validity_checker(s):  # Check if the new state is valid
                        continue
                
                # Check if the edge between the nearest vertex and the sampled state is valid
                if env.edge_validity_checker(s, nearest_vert[1]):
                    # Add the new state to the tree
                    s_idx = self.tree.add_vertex(s, nearest_vert)
                    cost = env.compute_distance(s, nearest_vert[1])  # Compute the cost of the edge
                    self.tree.add_edge(nearest_vert_idx, s_idx, cost)  # Add the edge to the tree

                    # If the sampled state is the goal and extension mode is E1, mark the goal as added
                    if goal and self.ext_mode == 'E1':
                        goal_added = True

                    # Update the number of nearest neighbors for rewiring in log mode
                    if log:
                        self.k = int(2 * np.log10(len(self.tree.vertices)))

                    # Perform the rewiring phase if the tree has more than k vertices
                    if len(self.tree.vertices) > self.k:
                        knn_idxs, knn_states = self.tree.get_k_nearest_neighbors(s, self.k)  # Get k nearest neighbors
                        for i in range(len(knn_states)):
                            if knn_idxs[i] == s_idx:  # Skip the current state
                                continue
                            if env.edge_validity_checker(knn_states[i], s):  # Check if the edge is valid
                                old_cost = self.tree.vertices[s_idx].cost
                                # Calculate the potential new cost for the sample
                                c = env.compute_distance(knn_states[i], s)
                                potential_parent_cost = self.tree.vertices[knn_idxs[i]].cost
                                potential_new_cost = potential_parent_cost + c
                                # Check for improvement
                                if potential_new_cost < old_cost:
                                    self.tree.vertices[s_idx].cost = potential_new_cost
                                    self.tree.edges[s_idx] = knn_idxs[i]
                                    num_rewires += 1
                        for i in range(len(knn_states)):
                            if knn_idxs[i] == s_idx:  # Skip the current state
                                continue
                            if env.edge_validity_checker(s, knn_states[i]):  # Check if the edge is valid
                                old_cost = self.tree.vertices[knn_idxs[i]].cost
                                # Calculate the potential new cost for the neighbors
                                c = env.compute_distance(s, knn_states[i])
                                potential_parent_cost = self.tree.vertices[s_idx].cost
                                potential_new_cost = potential_parent_cost + c
                                # Check for improvement
                                if potential_new_cost < old_cost:
                                    self.tree.vertices[knn_idxs[i]].cost = potential_new_cost
                                    self.tree.edges[knn_idxs[i]] = s_idx
                                    num_rewires += 1
                else:
                    goal_added = False  # Reset the goal flag if the edge is invalid
                    
        # Reconstruct the path if the goal was added
        if goal_added:
            plan.append(s)  # Add the goal state to the plan
            child_idx = s_idx
            parent_state = nearest_vert[1]
            while self.tree.edges[child_idx]:  # Traverse the tree to reconstruct the path
                plan.append(parent_state)
                child_idx = self.tree.get_idx_for_state(parent_state)
                # Get the new parent
                parent_idx = self.tree.edges[child_idx] 
                parent_state = self.tree.vertices[parent_idx].state
            plan.append(parent_state)  # Add the start state to the plan
        plan = plan[::-1]  # Reverse the plan to get it from start to goal

        # Print statistics
        print(f"Total number of iterations needed to reach goal: {num_iter}")
        print(f"Total number of rewirings conducted: {num_rewires}")

        # Print total path cost and time
        total_time = time.time() - start_time
        total_cost = self.compute_cost(plan)
        print('Total cost of path: {:.3f}'.format(total_cost))
        print('Total time: {:.3f} seconds'.format(total_time))
        #  itorite over the plan and print each step
        for i, step in enumerate(plan):
            print(f"Step {i}: {step}")

        return np.array(plan)

    def compute_cost(self, plan):
        '''
        Compute and return the plan cost, which is the sum of the distances between steps.
        @param plan A given plan for the robot.
        '''
        return self.tree.get_vertex_for_state(plan[-1]).cost  # Return the cost of the goal state

    def extend(self, near_state, rand_state):
        '''
        Compute and return a new position for the sampled one.
        @param near_state The nearest position to the sampled position.
        @param rand_state The sampled position.
        '''
        goal = False
        goal_state = self.planning_env.goal
        if (rand_state[0] == goal_state[0] and rand_state[1] == goal_state[1]):  # Check if the sampled state is the goal
            goal = True

        # Compute the vector from the nearest state to the sampled state
        vec = [rand_state[i] - near_state[i] for i in range(2)]
        vec_mag = np.sqrt(sum(j**2 for j in vec))  # Compute the magnitude of the vector
        unit_vec = vec / vec_mag  # Normalize the vector
        new_vec = self.step_size * unit_vec  # Scale the vector by the step size
        new_state = near_state + new_vec  # Compute the new state

        # Check if this intersects the goal or not
        goal_added = False
        if goal:
            if vec_mag < self.step_size:  # If the goal is within the step size, snap to the goal
                new_state = rand_state
                goal_added = True
        return new_state, goal_added
