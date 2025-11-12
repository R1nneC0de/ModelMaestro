import asyncio
from app.services.project_service import ProjectService

async def check_projects():
    service = ProjectService()
    projects_response = await service.list_projects(page_size=50)
    
    print(f'Total projects: {projects_response.total}\n')
    
    completed = [p for p in projects_response.projects if p.status.value == 'complete']
    print(f'Completed projects: {len(completed)}\n')
    
    if completed:
        for p in completed[:5]:  # Show first 5
            print(f'Project: {p.id}')
            print(f'  Status: {p.status}')
            print(f'  Model ID: {p.model_id}')
            print(f'  Vertex Model Resource: {getattr(p, "vertex_model_resource_name", "N/A")}')
            print(f'  Dataset: {p.dataset_id}')
            print()
    else:
        print('No completed projects found')
        print('\nAll project statuses:')
        status_counts = {}
        for p in projects_response.projects:
            status = p.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        for status, count in status_counts.items():
            print(f'  {status}: {count}')

asyncio.run(check_projects())
