"""CLI interface for SkillScope."""

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="jobscan", help="SkillScope CLI — career intelligence from job postings")
console = Console()


@app.command()
def import_paste(
    title: str = typer.Option("Untitled", help="Job title"),
    company: str = typer.Option(None, help="Company name"),
):
    """Import a job description from stdin (pipe or paste)."""
    import sys

    from app.db import SessionLocal
    from app.services.importer import import_text

    text = sys.stdin.read()
    if not text.strip():
        console.print("[red]No input received. Pipe a job description to stdin.[/red]")
        raise typer.Exit(1)

    db = SessionLocal()
    try:
        job = import_text(db, text, title, company)
        console.print(f"[green]Imported:[/green] {job.title} — {len(job.skill_occurrences)} skills found")
        for occ in job.skill_occurrences:
            console.print(f"  - {occ.skill.name} ({occ.skill.category.value})")
    finally:
        db.close()


@app.command()
def import_csv(path: str = typer.Argument(..., help="Path to CSV file")):
    """Import jobs from a CSV file."""
    from pathlib import Path

    from app.db import SessionLocal
    from app.services.importer import import_csv as do_import

    csv_path = Path(path)
    if not csv_path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        raise typer.Exit(1)

    db = SessionLocal()
    try:
        jobs = do_import(db, csv_path.read_text(encoding="utf-8"))
        console.print(f"[green]Imported {len(jobs)} jobs[/green]")
    finally:
        db.close()


@app.command()
def rankings(limit: int = typer.Option(20, help="Number of skills to show")):
    """Show top skills by demand."""
    from app.db import SessionLocal
    from app.services.analyzer import get_skill_rankings

    db = SessionLocal()
    try:
        results = get_skill_rankings(db, limit)
        if not results:
            console.print("[yellow]No data yet. Import some jobs first.[/yellow]")
            raise typer.Exit()

        table = Table(title="Top Skills by Demand")
        table.add_column("#", style="dim")
        table.add_column("Skill", style="bold cyan")
        table.add_column("Category")
        table.add_column("Jobs", justify="right")
        table.add_column("% of Jobs", justify="right")

        for i, r in enumerate(results, 1):
            table.add_row(str(i), r.name, r.category, str(r.count), f"{r.percentage}%")

        console.print(table)
    finally:
        db.close()


@app.command()
def gap(profile_id: int = typer.Argument(..., help="Your profile ID")):
    """Show gap analysis for your profile."""
    from app.db import SessionLocal
    from app.services.analyzer import get_gap_analysis

    db = SessionLocal()
    try:
        result = get_gap_analysis(db, profile_id)
        if not result:
            console.print("[red]Profile not found[/red]")
            raise typer.Exit(1)

        console.print(f"\n[bold]Match Score:[/bold] {result.match_percentage}%\n")

        if result.high_value_skills:
            console.print("[bold green]Your High-Value Skills:[/bold green]")
            for s in result.high_value_skills:
                console.print(f"  [green]✓[/green] {s}")

        if result.top_recommendations:
            console.print("\n[bold yellow]Learn Next:[/bold yellow]")
            for i, s in enumerate(result.top_recommendations, 1):
                console.print(f"  {i}. {s}")

        if result.undervalued_skills:
            console.print("\n[dim]Skills you have with low market demand:[/dim]")
            for s in result.undervalued_skills:
                console.print(f"  - {s}")
    finally:
        db.close()


if __name__ == "__main__":
    app()
