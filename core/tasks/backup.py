from nornir.core.task import Result, Task
from nornir_scrapli.tasks import send_command
from datetime import datetime
import os

def backup_device(task: Task, backup_dir: str = "backups") -> Result:
    """Task to backup the running configuration of a device."""
    
    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Send command via scrapli
    command = "show run"
    if task.host.platform == "junos":
        command = "show configuration"
        
    result = task.run(task=send_command, command=command)
    
    config_data = result.result
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{backup_dir}/{task.host.name}_{timestamp}.cfg"
    
    with open(filename, "w") as f:
        f.write(config_data)
        
    task.host.data["latest_backup"] = filename
    
    return Result(
        host=task.host,
        result={"config": config_data, "file": filename, "status": "backed_up"}
    )
