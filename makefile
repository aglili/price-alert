rs:
	@uvicorn app.api.main:app --reload      

ruff:
	@ruff check ./app

fix:	
	@ruff ./app --fix