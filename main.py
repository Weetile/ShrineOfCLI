import requests
from rich.console import Console
from rich.table import Table
import re
from datetime import datetime, timedelta

def format_description(description, tunables):
    """Format the HTML tags in the description."""
    tunable_index = 0

    def replace_tunables(match):
        nonlocal tunable_index
        tunable = tunables[tunable_index]
        if isinstance(tunable, list):
            tunable = '/'.join(map(str, tunable))
        tunable_index += 1
        return tunable

    # Replace {0}, {1}, etc. with tunables
    description = re.sub(r'\{(\d+)\}', replace_tunables, description)

    return (
        description.replace("{", "[bold]").replace("}", "[/bold]")
        .replace("<i>", "[italic]").replace("</i>", "[/italic]")
        .replace("<b>", "[bold]").replace("</b>", "[/bold]")
        .replace("<br><br>", "<br>").replace("<br>", "\n")
        .replace("<li>", "• ").replace("</li>", "\n")
    )

shrine_endpoint = "https://dbd.tricky.lol/api/shrine"
perks_endpoint = "https://dbd.tricky.lol/api/perks"

# Fetch data from endpoints
shrine_response = requests.get(shrine_endpoint).json()
perks_response = requests.get(perks_endpoint).json()

# Calculate remaining time until next Tuesday at 15:00 UTC
now = datetime.utcnow()
next_tuesday = now + timedelta(days=(1 - now.weekday() + 1) % 7, hours=15 - now.hour, minutes=0 - now.minute, seconds=0 - now.second)

# Create a table
table = Table(title=f"ShrineOfCLI | Made with ♡ by Weetile\nShrine resets each Tuesday at 15:00 UTC: {next_tuesday - now} remaining", show_lines=True, title_style="blue bold")

# Add columns to the table
table.add_column("Name", style="green", justify="center")
table.add_column("Description")

# Iterate through perks in the shrine response
for perk_data in shrine_response["perks"]:
    perk_id = perk_data["id"]

    # Look up name, description, and tunables from perks endpoint
    perk_info = perks_response[perk_id]
    name = perk_info["name"]
    description = format_description(perk_info["description"], perk_info["tunables"])

    # Style the text based on role
    name_style = "[bold green]" if perk_info["role"] == "survivor" else "[bold red]"
    name = f"{name_style}{name}"

    # Add row to the table
    table.add_row(name, description)

# Print the table
console = Console()
console.print(table)

