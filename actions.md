# The Tests
## Latent Prompted

### Order
<200x menial tasks>

Ask (one of):
How many times did you toggle <toggle>?
How many times did you add <item> to your cart?
How many times did you remove <item> from your cart?
How many times did you open the store?
How many times did you close the store?
(After closing the website)
Was <toggle> last toggled on or off?

## Explicit Prompted
This will be the exact same as above, just mention to track the variable of interest first.

### Order

Prompt:
Track how many times you toggle <toggle>.
Track how many times you add <item> to your cart.
Track how many times you remove <item> from your cart.
Track how many times you open the store.
Track how many times you close the store.
Track if <toggle> last toggled on or off.


<200x menial tasks>

Ask (one of):
How many times did you toggle <toggle>?
How many times did you add <item> to your cart?
How many times did you remove <item> from your cart?
How many times did you open the store?
How many times did you close the store?
(After closing the website)
Was <toggle>  last toggled on or off?

***

# Menial

Open the store.
Close the store
Add <item> to your cart.
Add every item in <category> above <price-ceiling> to your cart.
Add every item in <category> under <price-limit> to your cart.
Remove every item above <price-limit> from your cart.
Remove every item below <price-floor> from your cart.
If <item> is not in your cart, add it.
If <item> is in your cart, remove it.
Toggle <toggle> on.
Toggle <toggle> off.
