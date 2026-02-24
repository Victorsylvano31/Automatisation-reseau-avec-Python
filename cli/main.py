import typer
import requests
import json
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="NRE Platform CLI")
console = Console()
API_BASE_URL = "http://localhost:8000/api/v1"

@app.command()
def backup(site: str = typer.Option(None, help="Filter by site name")):
    """Trigger a backup job for all devices or filtered by site."""
    filters = {"site": site} if site else None
    
    with console.status("Triggering backup job..."):
        try:
            response = requests.post(f"{API_BASE_URL}/jobs/backup", json={"filters": filters})
            response.raise_for_status()
            data = response.json()
            console.print(f"[green]✔ Job triggered successfully![/green] Job ID: {data['job_id']}")
        except Exception as e:
            console.print(f"[red]❌ Failed to trigger job: {e}[/red]")

@app.command()
def status(job_id: str):
    """Check the status of a job."""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}")
        response.raise_for_status()
        data = response.json()
        
        table = Table(title="Job Status")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="magenta")
        for k, v in data.items():
            table.add_row(k, str(v))
            
        console.print(table)
    except Exception as e:
        console.print(f"[red]❌ Failed to get job status: {e}[/red]")

if __name__ == "__main__":
    app()
