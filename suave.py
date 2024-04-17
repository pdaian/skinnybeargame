""" SUAVE -- the only low latency domain that can run a decentralized action game today """

# TODO : make everything below this line actually SUAVE
# TODO : some kinda signup API

class SUAVE:
    MOCK_PLAYER_POSITIONS = {"alice": (0.0, 0.0), "bob": (10.0, 10.0)}
    CHAT_BUFFER = [(0, "alice", "hello world"), (1, "bob", "alice is noob"), (2, "alice", "no bob u r noob")]
    username = "FLASHBOT"

    def get_world(self):
        """ returns some randomly generated sparse-ish combo of ['cup', 'car', 'van', 'wellington', 'crate', 'sphere', 'grass', 'gravel', 'pigeon', 'blue_tree', 'pancake', 'kitty', 'entityspawner', 'explosion', 'tank', 'blacktop', 'player', 'objectexplosion', 'bullet'] """
        return open("pinehilldowntown_partial_parsed.csv").read()


    def get_player_positions(self):
        # todo mock this data
        return None

    def update_player_position(self, position):
        MOCK_PLAYER_POSITIONS[self.username] = position # send this to the syncd suave datastructure instead

    def send_chat_message(self, message):
        last_message_id = self.CHAT_BUFFER[-1][0]
        self.CHAT_BUFFER.append((last_message_id+1, self.username, message))

    def get_recent_chat_messages(self):
        if len(self.CHAT_BUFFER) > 100:
            self.CHAT_BUFFER = self.CHAT_BUFFER[-100:] # prune local buffer
        return self.CHAT_BUFFER
