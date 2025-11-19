import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from src.graph import app

console = Console()

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--use-flash-review', is_flag=True, help="Use the faster Gemini Flash model for the review step.")
def run(input_file, use_flash_review):
    """
    Runs the LangGraph-based patent translation system.
    """
    console.print(Panel("🚀 [bold blue]Starting Patent-Mind Translation System[/bold blue]"))

    with open(input_file, 'r', encoding='utf-8') as f:
        source_text = f.read()

    initial_state = {
        "original_text": source_text,
        "document_type": "claim", # Example, can be made dynamic
        "use_flash_review": use_flash_review,
        "messages": []
    }

    console.print(f"📄 Processing file: {input_file}")
    console.print(f"⚡ Using Flash for review: {'Yes' if use_flash_review else 'No'}")
    
    final_state = app.invoke(initial_state)

    translation = final_state.get("draft_translation", "No translation generated.")
    
    console.print(Panel("[bold green]✅ Translation Complete[/bold green]"))
    syntax = Syntax(translation, "text", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Final Translation", border_style="green"))

    review = final_state.get("review_result", {})
    if review:
        console.print(Panel(f"Review Passed: {review.get('passed')}\nFeedback: {review.get('feedback')}", title="QA Review", border_style="cyan"))

if __name__ == "__main__":
    run()
