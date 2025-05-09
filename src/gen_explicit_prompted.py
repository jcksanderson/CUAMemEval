import random
from gen_menial import Vars, MenialGenerator

class ExplicitPrompted:
    MAX_INJECTED_OCCURRENCES_PER_100 = 8 # Max occurrences for injection scaling

    def __init__(self, prompted: bool = True):
        self.QUESTIONS = (
            ('Track how many times you toggle <toggle>.', 'How many times did you toggle <toggle>?'),
            ('Track how many times you add <item> to your cart.', 'How many times did you add <item> to your cart?'),
            ('Track how many times you remove <item> from your cart.', 'How many times did you remove <item> from your cart?'),
            ('Track how many times you open the store.', 'How many times did you open the store?'),
            ('Track how many times you close the store.', 'How many times did you close the store?'),
            ('Track if <toggle> last toggled on or off.', '<close>Was <toggle> last toggled on?')
        )
        self.PROBABILITIES = (
            0.10,  # toggle count
            0.25,  # item add count
            0.35,  # item remove count
            0.10,  # open store count
            0.10,  # close store count
            0.10   # toggle last state
        )
        self.menial_gen = MenialGenerator() 
        self.prompted = prompted

        self.prompt_pair = None
        self.answer: int = -1 
        self.question_type: str = "" 
        self.specific_entity_tracked: str | None = None 

    def _parse_price_from_menial_action(self, menial_action, keyword_before, keyword_after=" from your cart"):
        try:
            start_index = menial_action.index(keyword_before) + len(keyword_before)
            end_index = menial_action.index(keyword_after, start_index)
            price_str = menial_action[start_index:end_index].strip()
            # Remove '$' if present before converting to float
            if price_str.startswith('$'):
                price_str = price_str[1:]
            return float(price_str)
        except (ValueError, IndexError) as e: # Added 'as e' for potentially more specific debugging if needed
            print(f"Warning: Could not parse price from menial action: '{menial_action}'. Extracted string: '{price_str if 'price_str' in locals() else 'N/A'}'. Error: {e}")
            return None

    def gen_test(self, num_menial: int) -> tuple[list[str], int]:
        close_store_before_final_question = False
        prompts = []
        
        raw_track_prompt, raw_question_prompt = random.choices(
            population=self.QUESTIONS, weights=self.PROBABILITIES, k=1
        )[0]

        current_track_prompt = raw_track_prompt
        current_question_prompt = raw_question_prompt
        self.specific_entity_tracked = None 

        # Determine question type and the specific entity being tracked
        if "<toggle>" in raw_track_prompt:
            chosen_toggle = random.choice(Vars.TOGGLE_LIST) 
            current_track_prompt = raw_track_prompt.replace("<toggle>", chosen_toggle)
            current_question_prompt = raw_question_prompt.replace("<toggle>", chosen_toggle)
            self.specific_entity_tracked = chosen_toggle
            if "how many times" in raw_track_prompt:
                self.question_type = "toggle_count"
                self.answer = 0
            elif "last toggled on or off" in raw_track_prompt:
                self.question_type = "toggle_last_state"
                self.answer = 0 # Default to 'off', 1 will mean 'on/yes'
        elif "<item>" in raw_track_prompt:
            items_with_prices = list(Vars.PRICES.keys())
            if not items_with_prices: 
                items_with_prices = Vars.ITEM_LIST 
            chosen_item = random.choice(items_with_prices)
            current_track_prompt = raw_track_prompt.replace("<item>", chosen_item)
            current_question_prompt = raw_question_prompt.replace("<item>", chosen_item)
            self.specific_entity_tracked = chosen_item
            self.answer = 0 
            if "add <item>" in raw_track_prompt:
                self.question_type = "item_add_count"
            elif "remove <item>" in raw_track_prompt:
                self.question_type = "item_remove_count"
        elif "open the store" in raw_track_prompt:
            self.question_type = "open_store_count"
            self.answer = 0
        elif "close the store" in raw_track_prompt:
            self.question_type = "close_store_count"
            self.answer = 0
        else:
            self.question_type = "unknown" 
            self.answer = -99 

        if "<close>" in current_question_prompt:
            current_question_prompt = current_question_prompt.replace("<close>", "")
            close_store_before_final_question = True
        
        self.prompt_pair = (current_track_prompt, current_question_prompt)
        if self.prompted:
            prompts.append(self.prompt_pair[0]) 

        menial_actions = self.menial_gen.gen(num_menial)

        # --- Start: Ensure specific item actions occur if tracking item add/remove count ---
        if self.specific_entity_tracked and \
           (self.question_type == "item_add_count" or self.question_type == "item_remove_count"):
            
            current_occurrences = 0
            action_to_inject = ""
            
            specific_action_add1 = f"Add {self.specific_entity_tracked} to your cart."
            specific_action_add2 = f"If {self.specific_entity_tracked} is not in your cart, add it."
            specific_action_remove1 = f"If {self.specific_entity_tracked} is in your cart, remove it."

            if self.question_type == "item_add_count":
                current_occurrences += menial_actions.count(specific_action_add1)
                current_occurrences += menial_actions.count(specific_action_add2)
                action_to_inject = random.choice([specific_action_add1, specific_action_add2])
            elif self.question_type == "item_remove_count":
                current_occurrences += menial_actions.count(specific_action_remove1)
                action_to_inject = specific_action_remove1
            
            desired_occurrences = 0
            if num_menial > 0:
                # Calculate a dynamic upper bound for occurrences based on num_menial
                # Scaled from 0-MAX_INJECTED_OCCURRENCES_PER_100 (e.g., 0-8 per 100)
                max_for_this_length = round(self.MAX_INJECTED_OCCURRENCES_PER_100 * (num_menial / 100.0))
                # Ensure max_for_this_length is not negative if num_menial is very small
                max_for_this_length = max(0, int(max_for_this_length)) 
                desired_occurrences = random.randint(0, max_for_this_length)

            needed_insertions = desired_occurrences - current_occurrences

            if needed_insertions > 0 and len(menial_actions) > 0:
                # Ensure we don't try to insert more than the available slots
                actual_insertions = min(needed_insertions, len(menial_actions)) 
                for _ in range(actual_insertions):
                    # Prefer to replace actions that are NOT the one we're trying to inject, if possible
                    # This is a simple random replacement for now.
                    idx_to_replace = random.randrange(len(menial_actions))
                    menial_actions[idx_to_replace] = action_to_inject
        # --- End: Ensure specific item actions ---


        # State trackers
        store_is_currently_open = False 
        last_action_on_specific_toggle_for_count = None # Stores "on" or "off"
        specific_item_is_in_cart = False # Tracks if the specific_entity_tracked (item) is in cart

        # Track answer through menial actions
        for menial_action in menial_actions:
            item_was_in_cart_before_this_action = specific_item_is_in_cart 

            # Update cart state for the specific_entity_tracked if it's an item
            if self.specific_entity_tracked and self.specific_entity_tracked in Vars.PRICES: 
                if menial_action == f"Add {self.specific_entity_tracked} to your cart." or \
                   menial_action == f"If {self.specific_entity_tracked} is not in your cart, add it.":
                    specific_item_is_in_cart = True
                elif menial_action == f"If {self.specific_entity_tracked} is in your cart, remove it.":
                    if specific_item_is_in_cart: 
                         specific_item_is_in_cart = False
                elif "Remove every item above " in menial_action and " from your cart" in menial_action:
                    price_floor = self._parse_price_from_menial_action(menial_action, "Remove every item above ")
                    if price_floor is not None and Vars.PRICES[self.specific_entity_tracked] > price_floor:
                        if specific_item_is_in_cart: 
                            specific_item_is_in_cart = False
                elif "Remove every item below " in menial_action and " from your cart" in menial_action:
                    price_ceiling = self._parse_price_from_menial_action(menial_action, "Remove every item below ")
                    if price_ceiling is not None and Vars.PRICES[self.specific_entity_tracked] < price_ceiling:
                        if specific_item_is_in_cart: 
                            specific_item_is_in_cart = False
            
            # Apply counting logic based on question type
            if self.question_type == "toggle_count" and self.specific_entity_tracked:
                action_on_target_toggle_on = f"Toggle {self.specific_entity_tracked} on."
                action_on_target_toggle_off = f"Toggle {self.specific_entity_tracked} off."
                if menial_action == action_on_target_toggle_on:
                    if last_action_on_specific_toggle_for_count != "on":
                        self.answer += 1
                    last_action_on_specific_toggle_for_count = "on"
                elif menial_action == action_on_target_toggle_off:
                    if last_action_on_specific_toggle_for_count != "off":
                        self.answer += 1
                    last_action_on_specific_toggle_for_count = "off"
            elif self.question_type == "toggle_last_state" and self.specific_entity_tracked:
                if f"Toggle {self.specific_entity_tracked} on." == menial_action:
                    self.answer = 1 
                elif f"Toggle {self.specific_entity_tracked} off." == menial_action:
                    self.answer = 0 
            elif self.question_type == "item_add_count" and self.specific_entity_tracked:
                if menial_action == f"Add {self.specific_entity_tracked} to your cart." or \
                   menial_action == f"If {self.specific_entity_tracked} is not in your cart, add it.":
                    self.answer += 1 
            elif self.question_type == "item_remove_count" and self.specific_entity_tracked:
                item_would_be_removed_by_this_action = False
                if menial_action == f"If {self.specific_entity_tracked} is in your cart, remove it.":
                    item_would_be_removed_by_this_action = True
                elif "Remove every item above " in menial_action and " from your cart" in menial_action:
                    price_floor = self._parse_price_from_menial_action(menial_action, "Remove every item above ")
                    if price_floor is not None and self.specific_entity_tracked in Vars.PRICES and \
                       Vars.PRICES[self.specific_entity_tracked] > price_floor:
                        item_would_be_removed_by_this_action = True
                elif "Remove every item below " in menial_action and " from your cart" in menial_action:
                    price_ceiling = self._parse_price_from_menial_action(menial_action, "Remove every item below ")
                    if price_ceiling is not None and self.specific_entity_tracked in Vars.PRICES and \
                       Vars.PRICES[self.specific_entity_tracked] < price_ceiling:
                        item_would_be_removed_by_this_action = True
                
                if item_would_be_removed_by_this_action and item_was_in_cart_before_this_action:
                    self.answer += 1
            elif self.question_type == "open_store_count":
                if menial_action == "Open the store.":
                    if not store_is_currently_open:
                        self.answer += 1
                    store_is_currently_open = True
                elif menial_action == "Close the store": 
                    store_is_currently_open = False
            elif self.question_type == "close_store_count":
                if menial_action == "Close the store": 
                    if store_is_currently_open: 
                        self.answer += 1
                    store_is_currently_open = False
                elif menial_action == "Open the store.":
                    store_is_currently_open = True
        
        prompts.extend(menial_actions) 

        if close_store_before_final_question:
            prompts.append("Close the store.") 
        
        prompts.append(self.prompt_pair[1]) 
        
        return (prompts, self.answer)


if __name__ == '__main__':
    tester = ExplicitPrompted()

    print("\n--- Example Test ---")
    test_prompts, actual_answer = tester.gen_test(num_menial=1009)
    print("Generated Prompts:")
    for i, p in enumerate(test_prompts):
        print(f"{i+1}. {p}")
    print(f"Tracked Answer: {actual_answer}")
    print(f"Question Type: {tester.question_type}, Entity: {tester.specific_entity_tracked}")

