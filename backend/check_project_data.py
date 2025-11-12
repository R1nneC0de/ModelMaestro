import asyncio
from app.services.project_service import ProjectService

async def check_project():
    service = ProjectService()
    project = await service.get_project('proj_ac32f6a299cb')
    if project:
        print('Project found:')
        print(f'  ID: {project.id}')
        print(f'  Status: {project.status}')
        print(f'  Model ID: {project.model_id}')
        print(f'  Dataset ID: {project.dataset_id}')
        print(f'  User ID: {project.user_id}')
    else:
        print('Project not found - trying to list all projects')
        projects = await service.list_projects(page_size=5)
        print(f'Found {projects.total} projects:')
        for p in projects.projects:
            print(f'  - {p.id}: {p.status} (model: {p.model_id})')

asyncio.run(check_project())
