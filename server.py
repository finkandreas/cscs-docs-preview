import asyncio
from io import BytesIO
import os
import shutil
import subprocess
import sys

from aiohttp import web

routes = web.RouteTableDef()

target_dir = sys.argv[1]
secret = ''
if len(sys.argv) > 2:
    print("Provided upload token as commandline argument is being used")
    secret = f'Bearer {sys.argv[2]}'
elif 'UPLOAD_TOKEN' in os.environ:
    print("Provided upload token from environment variable is being used")
    secret = f'Bearer {os.environ["UPLOAD_TOKEN"]}'
if secret == '':
    print("No upload token provided, either use it as second argument at startup or provide it in the environment variable UPLOAD_TOKEN")
    sys.exit(1)
sys.stdout.flush()

@routes.post("/upload")
async def handle_upload(request: web.Request) -> web.Response:
    pr_number = request.query.get("path", "")
    if pr_number == "":
        return web.Response(body="path query parameter missing", status=400)
    if request.headers.get("Authorization", "") != secret:
        return web.Response(body="Unauthorized", status=403)

    output_dir = os.path.join(target_dir, pr_number)
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)
    data = await request.content.read()
    sp = await asyncio.create_subprocess_shell(f'tar -xzf - -C {output_dir}', stdin=subprocess.PIPE, stdout=None, stderr=None)
    await sp.communicate(input=data)
    if sp.returncode != 0:
        return web.Response(body="Could not unpack input data. It must be a valid tar.gz archive", status=400)
    return web.Response(text=pr_number)

@routes.delete("/upload")
async def handle_upload(request: web.Request) -> web.Response:
    pr_number = request.query.get("path", "")
    if pr_number == "":
        return web.Response(body="path query parameter missing", status=400)
    if request.headers.get("Authorization", "") != secret:
        return web.Response(body="Unauthorized", status=403)

    output_dir = os.path.join(target_dir, pr_number)
    shutil.rmtree(output_dir, ignore_errors=True)
    return web.Response(text='ok')


@routes.post(path="/{key:.+}")
async def defHandler(request: web.Request) -> web.Response:
    print("Requested site ", request.path)
    return web.Response(status=404)

app = web.Application()
app.add_routes(routes)
web.run_app(app, port=81)
