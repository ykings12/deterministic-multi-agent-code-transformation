from typing import Dict, Callable, Any


class NodeEngine:
    """
    Node-based execution engine.

    Each step is a NODE.
    Flow is controlled via transitions.

    This mimics LangGraph behavior.
    """

    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}

    def add_node(self, name: str, func: Callable):
        """
        Register a node
        """
        self.nodes[name] = func

    def add_edge(self, from_node: str, to_node: str):
        """
        Define transition
        """
        self.edges[from_node] = to_node

    def run(self, start_node: str, state: Dict):
        """
        Execute graph starting from start_node
        """

        current = start_node

        while current:

            print(f"\n🔷 NODE: {current}")

            node_fn = self.nodes.get(current)

            if not node_fn:
                raise ValueError(f"Node not found: {current}")

            result = node_fn(state)

            # Node can override next step
            if isinstance(result, dict) and "next" in result:
                current = result["next"]
            else:
                current = self.edges.get(current)

        return state
