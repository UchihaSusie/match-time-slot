from collections import defaultdict, deque
from zoneinfo import ZoneInfo
from utils.time_paraser import parse_multi_day_slots

# ---------------------- NETWORK FLOW IMPLEMENTATION ----------------------

class MaxFlow:
   def __init__(self, nodes):
       """
       Initialize a flow network using an adjacency list.
       nodes: List of nodes in the graph.
       """
       self.graph = defaultdict(dict)
       self.nodes = nodes

   def add_edge(self, u, v, capacity):
       """
       Add an edge with capacity to the network.
       """
       self.graph[u][v] = capacity
       # Reverse edge with 0 capacity (for residual graph)
       self.graph[v][u] = 0 

   def bfs(self, source, sink, parent):
       """
       Find path using BFS. Return True if a path is found.
       """
       visited = {node: False for node in self.nodes}
       queue = deque([source])
       visited[source] = True

       while queue:
           u = queue.popleft()
           for v in self.graph[u]:
               if not visited[v] and self.graph[u][v] > 0:  # a valid path that we can go
                   queue.append(v)
                   visited[v] = True
                   parent[v] = u
                   if v == sink: # bfs will stop when it reaches the sink node
                       return True
       return False

   def ford_fulkerson(self, source, sink):
       """
       Find the maximum flow from source to sink using Ford-Fulkerson Algorithm.
       """
       parent = {}
       max_flow = 0

       while self.bfs(source, sink, parent):
           path_flow = float("Inf")
           v = sink

           # Find minimum residual capacity in path
           while v != source:
               u = parent[v]
               path_flow = min(path_flow, self.graph[u][v])
               v = u

           # Update residual capacities
           v = sink
           while v != source:
               u = parent[v]
               self.graph[u][v] -= path_flow
               self.graph[v][u] += path_flow
               v = u

           max_flow += path_flow

       return max_flow

# ---------------------- INTERVIEW SCHEDULING ----------------------

def schedule_interviews(candidates, recruiters, slot_length_minutes, max_interviews_per_candidate, max_interviews_per_recruiter):
   """
   Matches candidates and recruiters for interviews based on their availability using the Ford-Fulkerson algorithm.
   All time comparisons are done in UTC to ensure correct cross-timezone matching.
  
   Args:
       candidates: dictionary of candidates and their availability.
       recruiters: dictionary of recruiters and their availability.
       slot_length_minutes: fixed duration of each interview slot.
       max_interviews_per_candidate: maximum interviews allowed per candidate.
       max_interviews_per_recruiter: maximum interviews allowed per recruiter.

   Returns:
       A List of scheduled interviews as [candidate, recruiter, time_slot].
   """
  
   # Parse time slots, get datetime objects in original timezone
   candidate_slots = {cand: parse_multi_day_slots(data["availability"], slot_length_minutes, data["timezone"])
                      for cand, data in candidates.items()}
  
   recruiter_slots = {rec: parse_multi_day_slots(data["availability"], slot_length_minutes, data["timezone"])
                      for rec, data in recruiters.items()}
  
   # Create UTC version for each time slot and maintain mapping between original time slot and UTC time slot
   candidate_slots_utc = {}
   utc_to_original_map = {}
   
   for cand, slots in candidate_slots.items():
       candidate_slots_utc[cand] = set()
       for slot in slots:
           # Convert to UTC time
           slot_utc = slot.astimezone(ZoneInfo("UTC"))
           candidate_slots_utc[cand].add(slot_utc)
           # Record mapping from UTC -> original time
           utc_to_original_map[(cand, slot_utc)] = slot
   
   # Similarly process the recruiter's time slots
   recruiter_slots_utc = {}
   for rec, slots in recruiter_slots.items():
       recruiter_slots_utc[rec] = set()
       for slot in slots:
           slot_utc = slot.astimezone(ZoneInfo("UTC"))
           recruiter_slots_utc[rec].add(slot_utc)
  
   # Create flow network
   nodes = set(["source", "sink"]) | set(candidates.keys()) | set(recruiters.keys())
   flow_network = MaxFlow(nodes)

   # Connect source to candidates
   for cand in candidates:
       flow_network.add_edge("source", cand, max_interviews_per_candidate)

   # Connect recruiters to sink
   for rec in recruiters:
       flow_network.add_edge(rec, "sink", max_interviews_per_recruiter)

   # Connect candidates to recruiters in UTC timezone
   edges = []
   for cand, c_slots_utc in candidate_slots_utc.items():
       for rec, r_slots_utc in recruiter_slots_utc.items():
           # Find commonly available times in UTC
           common_slots_utc = c_slots_utc & r_slots_utc
           
           for slot_utc in common_slots_utc:
               flow_network.add_edge(cand, rec, 1)
               # Use candidate's original timezone time as the result
               original_slot = utc_to_original_map[(cand, slot_utc)]
               edges.append((cand, rec, original_slot))


   # Run maximum flow algorithm
   flow_network.ford_fulkerson("source", "sink")

   # Format results
   scheduled_interviews = []
   
   # Need to track interview count for each person
   candidate_counts = defaultdict(int)
   recruiter_counts = defaultdict(int)
   
   for cand, rec, slot in edges:
       # Check if this edge is used
       if flow_network.graph[rec][cand] > 0:
           # Key modification: Check if interview count limits are exceeded
           if (candidate_counts[cand] < max_interviews_per_candidate and
               recruiter_counts[rec] < max_interviews_per_recruiter):
               
               formatted_time = slot.strftime("%Y-%m-%d %H:%M %Z")
               scheduled_interviews.append([cand, rec, formatted_time])
               
               # Update counts
               candidate_counts[cand] += 1
               recruiter_counts[rec] += 1
               
   return scheduled_interviews



