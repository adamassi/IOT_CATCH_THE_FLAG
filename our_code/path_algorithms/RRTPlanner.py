import numpy as np
from path_algorithms.RRTTree import RRTTree
import time


class RRTPlanner(object):

    def __init__(self, planning_env, ext_mode, goal_prob):

        # set environment and search tree
        self.planning_env = planning_env
        self.tree = RRTTree(self.planning_env)

        # set search params
        self.ext_mode = ext_mode
        self.goal_prob = goal_prob
        self.nums_of_runs = 1          # added in order to provide statistical results (averages over 10 runs).

    def plan(self):
        '''
        Compute and return the plan. The function should return a numpy array containing the states (positions) of the robot.
        '''
        # TODO: Task 3
        avg_cost = 0
        avg_time = 0
        runs_num = self.nums_of_runs
        start_time = 0
        worse = float('-inf')
        best = float('inf')
        for cnt in range(runs_num):
            start_time = time.time()
            # initialize an empty plan.
            plan = []
            total_cost = 0
            total_time = 0
            env = self.planning_env
            self.tree = RRTTree(env)
            start_state = env.start             # initialize start state
            goal_state = env.goal               # initialize goal state
            root_id = self.tree.add_vertex(start_state)   # create first node in the tree
            new_id = root_id
            loop_time = 0
            while not self.tree.is_goal_exists(goal_state):
                # Sample a random state with goal bias 
                sampled_state = self.get_sample_state(goal_state)
                # Find the nearest state in the tree
                [nearest_neighbor_id, nearest_neighbor_state] = self.tree.get_nearest_state(sampled_state)
                if not env.state_validity_checker(nearest_neighbor_state):
                    continue
                added_state = self.extend(nearest_neighbor_state, sampled_state)

                # If valid, add vertex and compute cost and create edge
                if env.edge_validity_checker(nearest_neighbor_state, added_state):
                    new_id = self.tree.add_vertex(added_state)
                    cost = np.linalg.norm(added_state - nearest_neighbor_state)
                    self.tree.add_edge(nearest_neighbor_id, new_id, cost)
                    if np.linalg.norm(added_state - goal_state) < 1e-3:
                        break
            # Reconstruct the path from the goal to the start
            run_time = time.time() - start_time
            plan = self.generate_path(new_id)            
            total_cost = self.compute_cost(plan)

            
            # Print total path cost and time for each run
            # print('Total cost of path (run {}): {:.2f}'.format(cnt + 1, total_cost))
            print('Total time (run {}): {:.2f}'.format(cnt + 1, run_time))
            worse = max(total_cost, worse)
            best = min(total_cost, best)
            avg_cost += total_cost
            avg_time += run_time

        print('Calc plan for:')
        print(f'Goal prob: {self.goal_prob}')
        print(f'Extend mode: {self.ext_mode}')
        print(f'************statistics : best = {best}, worse = {worse}')
        if self.ext_mode == 'E2':
            print(f'tested eta: {self.eta}')
        avg_cost = avg_cost / float(runs_num)
        avg_time = avg_time / float(runs_num)
        print(f"\nAverage cost of path: {avg_cost}")
        
        return (np.array(plan))


    def compute_cost(self, plan):
        '''
        Compute and return the plan cost, which is the sum of the distances between steps.
        @param plan A given plan for the robot.
        '''
        # TODO: Task 3
        cost = 0
        cnt = 0
        env = self.planning_env
        while cnt < (len(plan) - 1):
            cost += env.compute_distance(start_state=plan[cnt], end_state=plan[cnt + 1])
            cnt += 1
        return cost


    def extend(self, near_state, rand_state):
        '''
        Compute and return a new position for the sampled one.
        @param near_state The nearest position to the sampled position.
        @param rand_state The sampled position.
        ''' 
        # TODO: Task 3
        # Check which mode is requested
        env = self.planning_env       
        # Compute the vector difference (delta) between the sampled point and the nearest state.
        delta = rand_state - near_state
        # Calculate the Euclidean distance between the sampled state and the nearest state.
        delta_norm = env.compute_distance(rand_state, near_state)
        
        if self.ext_mode == 'E1':
            return near_state if np.isclose(delta_norm, 0)  else rand_state
        elif self.ext_mode == 'E2':
            # we want to choose the best eta
            eta_vec = [5, 10, 15]
            # the best result was received when eta = 10
            tested_eta = eta_vec[0]
            self.eta = tested_eta

            # Handle the case where delta_norm is zero or very small
            if np.isclose(delta_norm, 0):
                direction_vec = np.zeros_like(delta)
            else:
                direction_vec = delta / delta_norm
            new_state = rand_state

            # If the distance is greater than eta, we move towards the sampled state
            if self.eta < delta_norm:
                new_state = near_state + self.eta * direction_vec
            return new_state
        else:
            # In case of wrong extended mode
            assert 0
    
        
    def generate_path(self, new_id):
        plan = []
        curr_state_id = new_id
        # Loop from goal vertex till we get to the root, and append to plan each vertex.
        while curr_state_id != self.tree.get_root_id():
            curr_state = self.tree.vertices[curr_state_id].state
            plan.append(curr_state)
            curr_state_id = self.tree.edges[curr_state_id]

        #insert the root
        plan.append(self.tree.vertices[curr_state_id].state)

        #reverse the plan so the root will be at the start.
        plan.reverse()
        return plan
        
    def get_sample_state(self, goal_state):
        env = self.planning_env
        valid = 0
        max_loop = 50000
        if np.random.rand() < self.goal_prob:
                    return goal_state
        for _ in range(max_loop):
            sampled_state = np.array([np.random.uniform(env.xlimit[0], env.xlimit[1]), np.random.uniform(env.ylimit[0], env.ylimit[1])])
            if  env.state_validity_checker(state = sampled_state):
                return sampled_state
        raise ValueError("Could not find a free sample after max_tries attempts.")