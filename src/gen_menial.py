import random
from parse_prices import json_to_item_price_dictionary

class Vars:
    PRICES = json_to_item_price_dictionary("prices.json")
    ITEM_LIST = tuple(PRICES.keys())
    TOGGLE_LIST = ('student discount', 'dark mode', 'international shipping')
    PRICE_LIST = ('$50', '$100', '$150', '$200')
    CATEGORY_LIST = ('All', 'Books', 'Electronics', 'Home', 'Kitchen', 'Music')

class MenialGenerator:
    ACTION_LIST = (
        'Open the store.',
        'Close the store',
        'Add <item> to your cart.',
        'Remove every item above <price-floor> from your cart.',
        'Remove every item below <price-ceiling> from your cart.',
        'If <item> is not in your cart, add it.',
        'If <item> is in your cart, remove it.',
        'Toggle <toggle> on.',
        'Toggle <toggle> off.'
    )
    # Dummy items/toggles for the MenialGenerator to use when filling its own templates
    INTERNAL_ITEMS = list(Vars.PRICES.keys()) # Use items that have prices for better testing
    INTERNAL_TOGGLES = Vars.TOGGLE_LIST

    def _fill_placeholders(self, action_template):
        action = action_template
        if "<item>" in action:
            action = action.replace("<item>", random.choice(self.INTERNAL_ITEMS))
        if "<toggle>" in action:
            action = action.replace("<toggle>", random.choice(self.INTERNAL_TOGGLES))
        if "<price-floor>" in action:
            # The dummy generator does not add '$'. If your real one does, the parser handles it.
            action = action.replace("<price-floor>", random.choice(Vars.PRICE_LIST))
        if "<price-ceiling>" in action:
            action = action.replace("<price-ceiling>", random.choice(Vars.PRICE_LIST))
        # Add other placeholder replacements if MenialGenerator handles them
        return action

    def gen(self, number: int) -> list[str]:
        """Generates a list of menial actions."""
        generated_menial_actions = []
        if not MenialGenerator.ACTION_LIST or number <= 0: # Added number <= 0 check
            return []
        for _ in range(number):
            template = random.choice(MenialGenerator.ACTION_LIST)
            generated_menial_actions.append(self._fill_placeholders(template))
        return generated_menial_actions

if __name__ == "__main__":
    menial_generator = MenialGenerator()
    print(menial_generator.gen(100))
