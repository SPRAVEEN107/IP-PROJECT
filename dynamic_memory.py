from typing import Optional
from dataclasses import dataclass

@dataclass
class AllocationResult:
    """Result of a memory allocation attempt."""
    success: bool
    start: Optional[int] = None
    allocated_size: Optional[int] = None
    chosen_block_size: Optional[int] = None
    message: str = ""

class MemoryBlock:
    """Represents a block of memory with size, start position, and allocation status."""
    def __init__(self, size: int, start: int, block_id: int, is_free: bool = True):
        self.size = size
        self.start = start
        self.id = block_id
        self.is_free = is_free
        # internal fragmentation tracking removed

    def __repr__(self):
        status = "FREE" if self.is_free else "ALLOCATED"
        return f"Block[{self.id}] @ {self.start} ({self.size} units) [{status}]"
    # removed leftover attributes

class MemoryManager:
    def __init__(self, total_size):
        import random
        self.total_size = total_size
        self.next_id = 1
        self.blocks = {}
        self.address_map = {}

        # Create 3-5 random-sized blocks that sum to total_size
        num_blocks = random.randint(3, 5)
        remaining_size = total_size
        current_address = 0

        # Generate n-1 random proportions that sum to 1 (if any)
        if num_blocks - 1 > 0:
            random_vals = [random.random() for _ in range(num_blocks - 1)]
            total_rand = sum(random_vals) or 1.0
            proportions = [p / total_rand for p in random_vals]
        else:
            proportions = []

        # Create blocks (store as simple dicts used by the rest of the code)
        for i in range(num_blocks):
            if i < num_blocks - 1:
                size = int(total_size * proportions[i])
                size = max(size, 1)  # Ensure minimum size of 1
            else:
                size = remaining_size if remaining_size > 0 else 1  # Last block gets remaining size

            self.blocks[self.next_id] = {
                "size": size,
                "free": True,
                "start": current_address
            }

            current_address += size
            remaining_size -= size
            self.next_id += 1

        print(f"Initialized memory with {total_size} units in {num_blocks} blocks.")
        self.display_memory()

    # ------------------------- ALLOCATION -------------------------
    def allocate(self, size, strategy='best'):
        free_blocks = [(bid, b) for bid, b in self.blocks.items() if b["free"]]

        if not free_blocks:
            print("No free blocks available.")
            return

        # Select block based on strategy
        if strategy == 'best':
            chosen = min((b for b in free_blocks if b[1]['size'] >= size), key=lambda x: x[1]['size'], default=None)
        elif strategy == 'worst':
            chosen = max((b for b in free_blocks if b[1]['size'] >= size), key=lambda x: x[1]['size'], default=None)
        elif strategy == 'first':
            chosen = next((b for b in sorted(free_blocks, key=lambda x: x[1]['start']) if b[1]['size'] >= size), None)
        else:
            print("Invalid strategy.")
            return

        if not chosen:
            print("Error: No suitable block found for allocation.")
            return

        block_id, block = chosen
        remaining = block["size"] - size
        block["size"] = size
        block["free"] = False

        # Split block if necessary
        if remaining > 0:
            new_block = {"size": remaining, "free": True, "start": block["start"] + size}
            self.blocks[self.next_id] = new_block
            self.next_id += 1

        print(f"Allocated {size} units using '{strategy}-fit' in Block {block_id}.")
        self.display_memory()

    # ------------------------- DEALLOCATION -------------------------
    def deallocate(self, block_id):
        if block_id not in self.blocks:
            print("Invalid Block ID.")
            return

        block = self.blocks[block_id]
        if block["free"]:
            print("Block is already free.")
            return

        block["free"] = True
        print(f"Deallocated Block {block_id}.")
        self.display_memory()

    # ------------------------- DISPLAY -------------------------
    def display_memory(self):
        blocks = sorted(self.blocks.items(), key=lambda x: x[1]["start"])
        print("\n--- Memory Layout ---")
        total_free = sum(b["size"] for _, b in self.blocks.items() if b["free"])
        total_allocated = sum(b["size"] for _, b in self.blocks.items() if not b["free"])
        # fragmentation metrics removed

        for bid, b in blocks:
            status = "Free" if b["free"] else "Allocated"
            print(f"  ID:{bid:<3} | {status:<10} | Size:{b['size']:<5} | Start:{b['start']}")

        print(f"\n> Total Allocated: {total_allocated}")
        print(f"> Total Free:      {total_free}")
        # fragmentation details removed
        print("---------------------\n")
