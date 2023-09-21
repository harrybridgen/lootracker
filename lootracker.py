import pygame
import sys
import time


class LootSplitter:
    def __init__(self):
        self.members = {}  # Dictionary to store information about raid members
        self.active_members = set()  # Set to store currently active raid members
        self.loot_log = []  # List to store loot drops

    def add_member(self, player_name):
        if player_name.strip() and player_name not in self.members:
            self.members[player_name] = {"loot_share": 0}
            return f"{player_name} added to the raid."
        else:
            return "Invalid player name. Please enter a valid name."

    def log_drop(self, item_name, gp_value):
        if item_name.strip() and gp_value >= 0:
            gp_value_int = int(gp_value)  # Convert GP value to an integer
            active_share = 0
            if self.active_members:
                active_share = gp_value_int // len(
                    self.active_members
                )  # Use integer division
            for player in self.active_members:
                self.members[player]["loot_share"] += active_share
            formatted_gp_value = "{:,}".format(gp_value_int)  # Format GP value with commas
            self.loot_log.append({"item": item_name, "value": gp_value_int})
            return f"{item_name} ({formatted_gp_value} GP) logged."
        else:
            return "Invalid input. Please enter a valid item name and GP value."


    def player_join(self, player_name):
        if player_name.strip():
            if player_name not in self.members:
                self.add_member(player_name)
            if player_name in self.active_members:
                self.active_members.remove(player_name)
            self.active_members.add(player_name)
            return f"{player_name} joined the raid."
        else:
            return "Invalid player name. Please enter a valid name."

    def player_leave(self, player_name):
        if player_name.strip() and player_name in self.members:
            if player_name in self.active_members:
                self.active_members.remove(player_name)
            return f"{player_name} left the raid."
        else:
            return "Invalid player name. Please enter a valid name."

    def split_loot(self):
        loot_shares = {}
        for player, info in self.members.items():
            loot_shares[player] = "{:,}".format(info["loot_share"])
            info["loot_share"] = 0  # Reset loot share for the next raid

        return loot_shares


# Initialize Pygame
pygame.init()
message_scroll = 0
party_scroll = 0
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
FONT_SIZE = 24

# Create a Pygame window
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Loot Splitter")

# Create a font object
font = pygame.font.Font(None, FONT_SIZE)

# Initialize LootSplitter
loot_splitter = LootSplitter()

# Input variables
command_input = ""
input_rect = pygame.Rect(10, 10, 300, 30)
input_active = False
input_color = pygame.Color("lightskyblue3")

ui_split = WINDOW_WIDTH * 0.6

# Message area
message_area = pygame.Rect(10, 50, ui_split, WINDOW_HEIGHT - 60)
message_bg_color = GRAY
message_color = BLACK
messages = []
max_messages = 17

# Party members list area
party_members_area = pygame.Rect(
    ui_split + 20, 50, WINDOW_WIDTH - ui_split - 30, WINDOW_HEIGHT - 60
)
party_members_bg_color = GRAY
party_members_color = BLACK


# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                input_active = True
            else:
                input_active = False
        if event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    # Process the entered command
                    if command_input:
                        command_parts = command_input.split()
                        command = command_parts[0].strip().lower()

                        if command == "join":
                            player_name = " ".join(command_parts[1:])
                            message = loot_splitter.player_join(player_name)

                        elif command == "log":
                            if loot_splitter.active_members.__len__() == 0:
                                message = "No active players. Please add players to the raid."
                            elif len(command_parts) >= 3:
                                item_name = command_parts[1]
                                try:
                                    gp_value = int(command_parts[2])
                                    message = loot_splitter.log_drop(
                                        item_name, gp_value
                                    )
                                except ValueError:
                                    message = "Invalid GP value. Please enter a valid number."
                            else:
                                message = "Invalid input. Please enter a valid item name and GP value."
                                
                        elif command == "leave":
                            player_name = " ".join(command_parts[1:])
                            message = loot_splitter.player_leave(player_name)

                        elif command == "split":
                            loot_shares = loot_splitter.split_loot()

                            message = "Loot Shares:\n"
                            for player, share in loot_shares.items():
                                message += f"{player} gets {share} GP\n"

                        elif command == "quit":
                            pygame.quit()
                            sys.exit()
                        else:
                            message = "Invalid command. Please enter a valid command."

                        messages.append(message)
                    command_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    command_input = command_input[:-1]
                else:
                    command_input += event.unicode
        if event.type == pygame.MOUSEWHEEL:
            # Check for scrolling in message area
            if message_area.collidepoint(pygame.mouse.get_pos()):
                if event.y > 0:  # Scrolling up
                    message_scroll = max(message_scroll - 1, 0)
                elif event.y < 0:  # Scrolling down
                    message_scroll = min(
                        message_scroll + 1, max(0, len(messages) - max_messages)
                    )
            # Check for scrolling in party members area
            if party_members_area.collidepoint(pygame.mouse.get_pos()):
                if event.y > 0:  # Scrolling up
                    party_scroll = max(party_scroll - 1, 0)
                elif event.y < 0:  # Scrolling down
                    party_scroll = min(
                        party_scroll + 1,
                        max(0, len(loot_splitter.members) - max_messages),
                    )

    # Clear the screen
    window.fill(WHITE)

    # Draw input box
    pygame.draw.rect(window, input_color, input_rect, 2)
    text_surface = font.render(command_input, True, BLACK)
    window.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

    # Draw message area
    pygame.draw.rect(window, message_bg_color, message_area)
    pygame.draw.rect(window, BLACK, message_area, 2)  # Add border
    text_surface = font.render("Messages", True, BLACK)
    window.blit(text_surface, (message_area.x + 10, message_area.y + 10))
    y_offset_message = 40  # Initialize y_offset for message area

    for message in messages[message_scroll : message_scroll + max_messages]:
        # Only render the visible portion based on message_scroll
        text_surface = font.render(message, True, BLACK)
        window.blit(
            text_surface, (message_area.x + 20, message_area.y + y_offset_message)
        )
        y_offset_message += 30

    # Update and draw party members area
    pygame.draw.rect(window, party_members_bg_color, party_members_area)
    pygame.draw.rect(window, BLACK, party_members_area, 2)  # Add border
    text_surface = font.render("Party Members", True, BLACK)
    window.blit(text_surface, (party_members_area.x + 10, party_members_area.y + 10))
    y_offset_party = 40  # Initialize y_offset for party members area

    # Convert the dict_items object to a list and then slice it
    party_members_list = list(loot_splitter.members.items())
    for player, info in party_members_list[party_scroll : party_scroll + max_messages]:
        # Only render the visible portion based on party_scroll
        loot_share = int(info["loot_share"])
        formatted_gp_value = "{:,}".format(loot_share)
        text_surface = font.render(f"{player}: {formatted_gp_value} GP", True, BLACK)
        window.blit(
            text_surface,
            (party_members_area.x + 20, party_members_area.y + y_offset_party),
        )
        y_offset_party += 30

    # Update the display
    pygame.display.flip()
