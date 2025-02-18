from fastapi import FastAPI, APIRouter

router = APIRouter(prefix="/api")

app = FastAPI(
    routes=router.routes,
    root_path="/notifications_service",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

@app.get("/")
def read_root():
    return {"Hello": "World"}