import socket
import threading
import time
import random
import logging

# Constants
ELECTION_TIMEOUT_MIN = 1.5  # seconds
ELECTION_TIMEOUT_MAX = 3.0  # seconds
HEARTBEAT_INTERVAL = 1  # seconds
VOTERS_REQUIRED = 2  # For simplicity, assume 3 nodes total

# Logger setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

# RAFT Node class
class RaftNode:
    def __init__(self, node_id, nodes):
        self.node_id = node_id
        self.nodes = nodes  # List of other nodes
        self.state = 'Follower'
        self.voted_for = None
        self.vote_count = 0
        self.election_timeout = random.uniform(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.heartbeat_received = False

    def start(self):
        """Start the node simulation."""
        logging.info(f"Node {self.node_id} started as a Follower.")
        while True:
            if self.state == 'Follower':
                self.run_follower()
            elif self.state == 'Candidate':
                self.run_candidate()
            elif self.state == 'Leader':
                self.run_leader()

    def run_follower(self):
        """Follower logic: Wait for heartbeat or election timeout."""
        self.heartbeat_received = False
        start_time = time.time()
        while time.time() - start_time < self.election_timeout:
            if self.heartbeat_received:
                self.reset_election_timeout()
                return
            time.sleep(0.1)
        self.start_election()

    def run_candidate(self):
        """Candidate logic: Start election and request votes."""
        self.vote_count = 1  # Candidate always votes for itself
        self.voted_for = self.node_id
        self.broadcast_vote_request()
        self.wait_for_votes()

    def run_leader(self):
        """Leader logic: Send heartbeats to followers."""
        while True:
            self.send_heartbeats()
            time.sleep(HEARTBEAT_INTERVAL)

    def start_election(self):
        """Start the election process."""
        self.state = 'Candidate'
        self.voted_for = self.node_id
        self.vote_count = 1
        logging.info(f"Node {self.node_id} is starting an election.")
        self.broadcast_vote_request()

    def broadcast_vote_request(self):
        """Broadcast the vote request to other nodes."""
        for node in self.nodes:
            if node != self.node_id:
                self.send_vote_request(node)

    def send_vote_request(self, node):
        """Send a vote request to a node."""
        message = f"VoteRequest {self.node_id}"
        self.send_message(node, message)

    def send_vote_response(self, candidate_id):
        """Send a vote response message to the candidate."""
        message = f"VoteResponse {self.node_id} {candidate_id}"
        self.send_message(candidate_id, message)

    def send_heartbeats(self):
        """Send heartbeat messages to followers."""
        for node in self.nodes:
            if node != self.node_id:
                self.send_message(node, f"Heartbeat {self.node_id}")

    def send_message(self, node, message):
        """Send a UDP message to a node."""
        address = ('localhost', 5000 + int(node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), address)

    def wait_for_votes(self):
        """Wait for votes from other nodes."""
        start_time = time.time()
        while time.time() - start_time < self.election_timeout:
            if self.vote_count >= VOTERS_REQUIRED:
                self.become_leader()
                return
            time.sleep(0.1)
        self.state = 'Follower'  # If timeout occurs, go back to Follower

    def become_leader(self):
        """Become the leader after receiving enough votes."""
        self.state = 'Leader'
        logging.info(f"Node {self.node_id} has become the Leader.")

    def reset_election_timeout(self):
        """Reset the election timeout when heartbeat is received."""
        self.election_timeout = random.uniform(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.state = 'Follower'

    def handle_message(self, message):
        """Handle incoming messages (vote requests and heartbeats)."""
        if message.startswith("VoteRequest"):
            candidate_id = message.split()[1]
            if self.state == 'Follower' and self.voted_for is None:
                self.voted_for = candidate_id
                self.send_vote_response(candidate_id)

        elif message.startswith("VoteResponse"):
            # Handle vote response (e.g., counting votes in Candidate state)
            if self.state == 'Candidate':
                self.vote_count += 1

        elif message.startswith("Heartbeat"):
            if self.state != 'Leader':
                self.reset_election_timeout()

    def listen(self):
        """Listen for incoming messages."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('localhost', 5000 + self.node_id))
            while True:
                data, _ = sock.recvfrom(1024)
                message = data.decode()
                self.handle_message(message)

# Main function to start multiple nodes
def start_node(node_id, nodes):
    node = RaftNode(node_id, nodes)
    threading.Thread(target=node.start).start()
    threading.Thread(target=node.listen).start()

if __name__ == "__main__":
    # Initialize 3 nodes
    node_count = 3
    nodes = list(range(node_count))

    # Start the nodes
    for node_id in nodes:
        start_node(node_id, nodes)
