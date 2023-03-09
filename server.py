from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import StreamingResponse, HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
import asyncio


app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get('/{id}/view', response_class=HTMLResponse)
async def view_stream(id: str, request: Request):
    return templates.TemplateResponse('view.html', {'request': request, 'id': id})


class StreamClient:
    def __init__(self, id: str):
        self.queue = asyncio.Queue(256)
        self.id = id

    def write(self, data):
        try:
            self.queue.put_nowait(data)
        except asyncio.QueueFull:
            pass

    async def read(self):
        while True:
            data = await self.queue.get()
            yield data
            self.queue.task_done()


streams: set[str] = set()
clients: list[StreamClient] = []


@app.post('/{id}')
async def post_stream(id: str, request: Request):
    if id in streams:
        return PlainTextResponse('Stream already exists', status_code=status.HTTP_409_CONFLICT)
    streams.add(id)
    print(f'Stream created: {id}')
    try:
        async for data in request.stream():
            for client in clients:
                if client.id == id:
                    client.write(data)
    finally:
        print(f'Stream closed: {id}')
        streams.remove(id)
        return PlainTextResponse('Stream closed')


@app.get('/{id}')
async def get_stream(id: str):
    if id not in streams:
        return PlainTextResponse('Stream does not exist', status_code=status.HTTP_404_NOT_FOUND)
    client = StreamClient(id)
    clients.append(client)
    print(f'Client connected: {id}')
    async def generate():
        try:
            async for data in client.read():
                yield data
        finally:
            print(f'Client disconnected: {id}')
            clients.remove(client)
    return StreamingResponse(generate(), media_type='multipart/x-mixed-replace;boundary=frame')
        
