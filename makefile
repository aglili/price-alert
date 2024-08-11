rs:
	@uvicorn app.api.main:app --reload      

ruff:
	@ruff check ./app

fix:	
	@ruff check ./app --fix


isort:
	@isort ./app


fmt:
	@black ./app